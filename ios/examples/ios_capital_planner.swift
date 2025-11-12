// iOS Swift Example: Capital Jump Planner
// Demonstrates how to build a jump planning UI using EVE Map API

import SwiftUI
import Combine

// MARK: - Models

struct CapitalShip: Codable, Identifiable {
    let ship_type_id: Int
    let ship_name: String
    let ship_class: String
    let base_range: Float
    let max_range_with_skills: Float
    let fuel_capacity: Int

    var id: Int { ship_type_id }
}

struct ShipDetails: Codable {
    let ship_type_id: Int
    let ship_name: String
    let ship_class: String
    let base_range_ly: Float
    let mass_kg: Int
    let fuel_capacity_units: Int
    let fuel_consumption_per_ly: Float
    let ranges_by_skill: [String: Float]
}

struct JumpLeg: Codable {
    let origin_system_id: Int
    let origin_name: String
    let destination_system_id: Int
    let destination_name: String
    let distance_ly: Float
    let fuel_consumed: Float
    let duration_minutes: Int
}

struct JumpChain: Codable {
    let origin_system_id: Int
    let destination_system_id: Int
    let legs: [JumpLeg]
    let total_distance_ly: Float
    let total_fuel_consumed: Float
    let total_duration_hours: Float
    let total_jumps: Int
    let requires_refuel: Bool
    let refuel_points: [Int]
}

struct JumpSphere: Codable {
    struct SystemInfo: Codable {
        let id: Int
        let name: String
        let distance_ly: Float
        let region_id: Int
        let security: Float
    }

    let origin_system_id: Int
    let origin_name: String
    let max_range_ly: Float
    let systems_in_range: [SystemInfo]
    let count: Int
}

// MARK: - API Client Extensions

extension EVEMapClient {

    func getCapitalShips() -> AnyPublisher<[CapitalShip], Error> {
        let url = baseURL.appendingPathComponent("capital/ships")

        struct Response: Codable {
            let ships: [CapitalShip]
        }

        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: Response.self, decoder: JSONDecoder())
            .map { $0.ships }
            .eraseToAnyPublisher()
    }

    func getShipDetails(shipTypeId: Int) -> AnyPublisher<ShipDetails, Error> {
        let url = baseURL.appendingPathComponent("capital/ships/\(shipTypeId)")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: ShipDetails.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func planJumpChain(
        origin: Int,
        destination: Int,
        shipTypeId: Int,
        skills: [String: Int],
        avoidLowsec: Bool = false
    ) -> AnyPublisher<JumpChain, Error> {
        let url = baseURL.appendingPathComponent("capital/jump-chain")

        let requestBody: [String: Any] = [
            "origin": origin,
            "destination": destination,
            "ship_type_id": shipTypeId,
            "skills": skills,
            "avoid_lowsec": avoidLowsec,
            "avoid_systems": [],
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: requestBody)

        return URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .decode(type: JumpChain.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func calculateJumpSphere(
        origin: Int,
        shipTypeId: Int,
        skills: [String: Int]
    ) -> AnyPublisher<JumpSphere, Error> {
        let url = baseURL.appendingPathComponent("capital/jump-sphere")

        let requestBody: [String: Any] = [
            "origin": origin,
            "ship_type_id": shipTypeId,
            "skills": skills,
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: requestBody)

        return URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .decode(type: JumpSphere.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
}

// MARK: - SwiftUI Views

struct CapitalPlannerView: View {
    @StateObject private var client = EVEMapClient()
    @State private var ships: [CapitalShip] = []
    @State private var selectedShip: CapitalShip?
    @State private var originSystem = ""
    @State private var destinationSystem = ""
    @State private var skillLevels: [String: Int] = [
        "advanced_spaceship_command": 5
    ]
    @State private var plannedRoute: JumpChain?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationView {
            Form {
                // Ship Selection
                Section(header: Text("Ship Selection")) {
                    Picker("Capital Ship", selection: $selectedShip) {
                        Text("Select a ship...").tag(Optional<CapitalShip>(nil))
                        ForEach(ships) { ship in
                            Text("\(ship.ship_name) (\(ship.ship_class))")
                                .tag(Optional(ship))
                        }
                    }

                    if let selected = selectedShip {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Base Range: \(selected.base_range, specifier: "%.1f") LY")
                                .font(.caption)
                            Text("Max Range: \(selected.max_range_with_skills, specifier: "%.1f") LY")
                                .font(.caption)
                                .fontWeight(.semibold)
                            Text("Fuel Capacity: \(selected.fuel_capacity) units")
                                .font(.caption)
                        }
                        .padding(.top, 8)
                    }
                }

                // Skills
                Section(header: Text("Skills")) {
                    HStack {
                        Text("Advanced Spaceship Command")
                        Spacer()
                        Stepper(
                            value: Binding(
                                get: { skillLevels["advanced_spaceship_command"] ?? 0 },
                                set: { skillLevels["advanced_spaceship_command"] = $0 }
                            ),
                            in: 0...5
                        )
                        Text("\(skillLevels["advanced_spaceship_command"] ?? 0)")
                            .frame(minWidth: 20)
                    }
                }

                // Route Planning
                Section(header: Text("Route Planning")) {
                    TextField("Origin System (ID)", text: $originSystem)
                        .keyboardType(.numberPad)

                    TextField("Destination System (ID)", text: $destinationSystem)
                        .keyboardType(.numberPad)

                    Button(action: planRoute) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            }
                            Text("Plan Jump Route")
                                .frame(maxWidth: .infinity, alignment: .center)
                        }
                    }
                    .disabled(isLoading || selectedShip == nil || originSystem.isEmpty || destinationSystem.isEmpty)
                }

                // Error Display
                if let error = errorMessage {
                    Section(header: Text("Error")) {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
            }
            .navigationTitle("Capital Jump Planner")
            .onAppear(perform: loadShips)
            .sheet(item: .constant(plannedRoute)) { route in
                RouteDetailView(route: route)
            }
        }
    }

    private func loadShips() {
        client.getCapitalShips()
            .receive(on: DispatchQueue.main)
            .sink { completion in
                if case .failure(let error) = completion {
                    errorMessage = error.localizedDescription
                }
            } receiveValue: { ships in
                self.ships = ships
            }
            .store(in: &client.cancellables)
    }

    private func planRoute() {
        guard let ship = selectedShip,
              let origin = Int(originSystem),
              let destination = Int(destinationSystem) else {
            errorMessage = "Invalid input"
            return
        }

        isLoading = true
        errorMessage = nil

        client.planJumpChain(
            origin: origin,
            destination: destination,
            shipTypeId: ship.ship_type_id,
            skills: skillLevels
        )
        .receive(on: DispatchQueue.main)
        .sink { completion in
            isLoading = false
            if case .failure(let error) = completion {
                errorMessage = "Route planning failed: \(error.localizedDescription)"
            }
        } receiveValue: { route in
            self.plannedRoute = route
        }
        .store(in: &client.cancellables)
    }
}

struct RouteDetailView: View {
    let route: JumpChain
    @Environment(\.presentationMode) var presentationMode

    var body: some View {
        NavigationView {
            VStack {
                // Summary
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Total Jumps")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text("\(route.total_jumps)")
                                .font(.headline)
                        }
                        Spacer()
                        VStack(alignment: .leading) {
                            Text("Distance")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(String(format: "%.2f LY", route.total_distance_ly))
                                .font(.headline)
                        }
                        Spacer()
                        VStack(alignment: .leading) {
                            Text("Fuel Required")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(String(format: "%.0f", route.total_fuel_consumed))
                                .font(.headline)
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)

                    if route.requires_refuel {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                            Text("Refueling required at \(route.refuel_points.count) station(s)")
                                .font(.caption)
                        }
                        .padding(.vertical, 8)
                    }
                }
                .padding()

                // Jump Legs
                List {
                    Section(header: Text("Jump Route")) {
                        ForEach(Array(route.legs.enumerated()), id: \.offset) { index, leg in
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Jump \(index + 1)")
                                    .font(.headline)

                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(leg.origin_name)
                                            .font(.subheadline)
                                            .fontWeight(.semibold)
                                        Text("↓")
                                            .font(.caption)
                                        Text(leg.destination_name)
                                            .font(.subheadline)
                                            .fontWeight(.semibold)
                                    }

                                    Spacer()

                                    VStack(alignment: .trailing, spacing: 4) {
                                        Text(String(format: "%.2f LY", leg.distance_ly))
                                            .font(.caption)
                                            .foregroundColor(.blue)
                                        Text(String(format: "%.0f fuel", leg.fuel_consumed))
                                            .font(.caption)
                                            .foregroundColor(.orange)
                                    }
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Preview

#if DEBUG
struct CapitalPlannerView_Previews: PreviewProvider {
    static var previews: some View {
        CapitalPlannerView()
    }
}
#endif
