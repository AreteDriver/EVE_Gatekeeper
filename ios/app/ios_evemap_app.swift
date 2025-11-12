// EVE Map iOS App - Production Ready
// Complete app combining system search, route planning, and capital jump planner
// Ready for App Store submission

import SwiftUI
import Combine

// MARK: - App Entry Point

@main
struct EVEMapApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            if appState.isInitialized {
                ContentView()
                    .environmentObject(appState)
            } else {
                SplashScreen()
                    .environmentObject(appState)
            }
        }
    }
}

// MARK: - App State & ViewModel

class AppState: ObservableObject {
    @Published var isInitialized = false
    @Published var apiURL: String {
        didSet {
            UserDefaults.standard.set(apiURL, forKey: "apiURL")
        }
    }
    @Published var shipConfigs: [ShipConfig] = []
    @Published var universalGraphCache: Data?

    private let client = EVEMapClient()

    init() {
        // Load saved API URL
        let savedURL = UserDefaults.standard.string(forKey: "apiURL") ?? "http://localhost:8000"
        self.apiURL = savedURL

        // Load ship configs
        if let saved = UserDefaults.standard.data(forKey: "shipConfigs"),
           let decoded = try? JSONDecoder().decode([ShipConfig].self, from: saved) {
            self.shipConfigs = decoded
        }

        // Initialize on background thread
        DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) {
            DispatchQueue.main.async {
                self.isInitialized = true
            }
        }
    }

    func saveShipConfig(_ config: ShipConfig) {
        if !shipConfigs.contains(where: { $0.id == config.id }) {
            shipConfigs.append(config)
        }
        persistShipConfigs()
    }

    func deleteShipConfig(_ config: ShipConfig) {
        shipConfigs.removeAll { $0.id == config.id }
        persistShipConfigs()
    }

    private func persistShipConfigs() {
        if let encoded = try? JSONEncoder().encode(shipConfigs) {
            UserDefaults.standard.set(encoded, forKey: "shipConfigs")
        }
    }

    func downloadUniverseGraph() -> AnyPublisher<Void, Error> {
        client.downloadGraph()
            .map { url in
                if let data = try? Data(contentsOf: url) {
                    self.universalGraphCache = data
                }
            }
            .eraseToAnyPublisher()
    }
}

// MARK: - Models

struct ShipConfig: Codable, Identifiable {
    let id: String
    var shipName: String
    var shipTypeId: Int
    var skills: [String: Int]

    init(shipName: String, shipTypeId: Int, skills: [String: Int] = [:]) {
        self.id = UUID().uuidString
        self.shipName = shipName
        self.shipTypeId = shipTypeId
        self.skills = skills
    }
}

struct SystemSearchResult: Codable, Identifiable {
    let id: Int
    let name: String
    let region_id: Int
    let security: Float
    let sec_class: String
}

// MARK: - Splash/Loading Screen

struct SplashScreen: View {
    var body: some View {
        ZStack {
            Color.black
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Image(systemName: "location.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.blue)

                Text("EVE Map")
                    .font(.system(size: 36, weight: .bold, design: .default))
                    .foregroundColor(.white)

                Text("New Eden Navigation System")
                    .font(.caption)
                    .foregroundColor(.gray)

                ProgressView()
                    .tint(.blue)
                    .padding(.top, 20)
            }
        }
    }
}

// MARK: - Main Content View

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            // Map & Search Tab
            MapSearchTab()
                .tabItem {
                    Label("Map", systemImage: "map.fill")
                }
                .tag(0)

            // Route Planner Tab
            RoutePlannerTab()
                .tabItem {
                    Label("Routes", systemImage: "arrow.triangle.2.circlepath")
                }
                .tag(1)

            // Capital Planner Tab
            CapitalPlannerTab()
                .tabItem {
                    Label("Capital", systemImage: "airplane.circle.fill")
                }
                .tag(2)

            // Settings Tab
            SettingsTab()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(3)
        }
        .accentColor(.blue)
    }
}

// MARK: - Map & Search Tab

struct MapSearchTab: View {
    @StateObject private var client = EVEMapClient()
    @State private var searchText = ""
    @State private var searchResults: [SystemSearchResult] = []
    @State private var selectedSystem: SystemSearchResult?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search Bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gray)

                    TextField("Search systems...", text: $searchText)
                        .onSubmit(performSearch)

                    if !searchText.isEmpty {
                        Button(action: { searchText = "" }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.gray)
                        }
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color(.systemGray6))
                .cornerRadius(8)
                .padding()

                // Results
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding()
                } else if let error = errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.title2)
                            .foregroundColor(.orange)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                } else if searchResults.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "globe")
                            .font(.title)
                            .foregroundColor(.gray)
                        Text("Search for systems")
                            .foregroundColor(.gray)
                        Text("Type a system name (e.g., 'Jita', 'Amarr')")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                } else {
                    List(searchResults) { system in
                        NavigationLink(destination: SystemDetailView(system: system, client: client)) {
                            VStack(alignment: .leading, spacing: 4) {
                                HStack {
                                    Text(system.name)
                                        .font(.headline)

                                    Spacer()

                                    SecurityBadge(secClass: system.sec_class)
                                }

                                HStack {
                                    Text("Security: \(String(format: "%.1f", system.security))")
                                        .font(.caption)
                                        .foregroundColor(.gray)

                                    Spacer()

                                    Text("Region \(system.region_id)")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                            }
                        }
                    }
                }

                Spacer()
            }
            .navigationTitle("New Eden")
        }
    }

    private func performSearch() {
        guard !searchText.isEmpty else {
            searchResults = []
            return
        }

        isLoading = true
        errorMessage = nil

        client.searchSystems(query: searchText)
            .receive(on: DispatchQueue.main)
            .sink { completion in
                isLoading = false
                if case .failure(let error) = completion {
                    errorMessage = error.localizedDescription
                }
            } receiveValue: { results in
                self.searchResults = results.map { system in
                    SystemSearchResult(
                        id: system.id,
                        name: system.name,
                        region_id: system.region_id,
                        security: system.security,
                        sec_class: system.sec_class
                    )
                }
            }
            .store(in: &client.cancellables)
    }
}

// MARK: - System Detail View

struct SystemDetailView: View {
    let system: SystemSearchResult
    let client: EVEMapClient
    @State private var neighbors: [System] = []
    @State private var isLoading = true

    var body: some View {
        VStack {
            List {
                Section(header: Text("System Information")) {
                    DetailRow(label: "System ID", value: "\(system.id)")
                    DetailRow(label: "Name", value: system.name)
                    DetailRow(label: "Region ID", value: "\(system.region_id)")
                    DetailRow(label: "Security", value: String(format: "%.1f", system.security))
                    DetailRow(label: "Class", value: system.sec_class)
                }

                if !neighbors.isEmpty {
                    Section(header: Text("Adjacent Systems (1 Jump)")) {
                        ForEach(neighbors) { neighbor in
                            VStack(alignment: .leading, spacing: 2) {
                                HStack {
                                    Text(neighbor.name)
                                        .font(.headline)
                                    Spacer()
                                    SecurityBadge(secClass: neighbor.sec_class)
                                }
                                Text("Security: \(String(format: "%.1f", neighbor.security))")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                }
            }
        }
        .navigationTitle(system.name)
        .onAppear(perform: loadNeighbors)
    }

    private func loadNeighbors() {
        client.getSystemNeighbors(id: system.id)
            .receive(on: DispatchQueue.main)
            .sink { _ in
                isLoading = false
            } receiveValue: { neighbors in
                self.neighbors = neighbors
            }
            .store(in: &client.cancellables)
    }
}

// MARK: - Route Planner Tab

struct RoutePlannerTab: View {
    @StateObject private var client = EVEMapClient()
    @State private var originText = ""
    @State private var destinationText = ""
    @State private var avoidLowsec = false
    @State private var plannedRoute: RouteResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Route Planning")) {
                    TextField("Origin System ID", text: $originText)
                        .keyboardType(.numberPad)

                    TextField("Destination System ID", text: $destinationText)
                        .keyboardType(.numberPad)

                    Toggle("Avoid Low-Sec", isOn: $avoidLowsec)
                }

                Section {
                    Button(action: planRoute) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            }
                            Text("Plan Route")
                                .frame(maxWidth: .infinity, alignment: .center)
                        }
                    }
                    .disabled(isLoading || originText.isEmpty || destinationText.isEmpty)
                }

                if let error = errorMessage {
                    Section(header: Text("Error")) {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }

                if let route = plannedRoute {
                    Section(header: Text("Route Result")) {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text("Total Jumps")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                    Text("\(route.jumps)")
                                        .font(.headline)
                                }
                                Spacer()
                                VStack(alignment: .leading) {
                                    Text("Security Profile")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                    Text(route.security_profile)
                                        .font(.headline)
                                }
                            }

                            Divider()

                            Text("Route:")
                                .font(.headline)
                            ForEach(Array(route.systems.enumerated()), id: \.offset) { index, system in
                                HStack {
                                    Text("\(index + 1).")
                                        .foregroundColor(.gray)
                                    Text(system)
                                    if index < route.systems.count - 1 {
                                        Spacer()
                                        Image(systemName: "arrow.right")
                                            .foregroundColor(.blue)
                                    }
                                }
                                .font(.caption)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                }
            }
            .navigationTitle("Route Planner")
        }
    }

    private func planRoute() {
        guard let origin = Int(originText),
              let destination = Int(destinationText) else {
            errorMessage = "Invalid system IDs"
            return
        }

        isLoading = true
        errorMessage = nil

        client.planRoute(origin: origin, destination: destination, avoidLowsec: avoidLowsec)
            .receive(on: DispatchQueue.main)
            .sink { completion in
                isLoading = false
                if case .failure(let error) = completion {
                    errorMessage = error.localizedDescription
                }
            } receiveValue: { route in
                self.plannedRoute = route
            }
            .store(in: &client.cancellables)
    }
}

// MARK: - Capital Planner Tab

struct CapitalPlannerTab: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var client = EVEMapClient()
    @State private var ships: [CapitalShip] = []
    @State private var selectedShip: CapitalShip?
    @State private var shipConfigs: [ShipConfig] = []
    @State private var selectedConfig: ShipConfig?
    @State private var originText = ""
    @State private var destinationText = ""
    @State private var plannedChain: JumpChain?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showNewConfigSheet = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Ship Selection")) {
                    Picker("Ship Preset", selection: $selectedConfig) {
                        Text("Create new...").tag(Optional<ShipConfig>(nil))
                        Divider()
                        ForEach(appState.shipConfigs) { config in
                            Text("\(config.shipName) (\(config.shipTypeId))")
                                .tag(Optional(config))
                        }
                    }
                    .onChange(of: selectedConfig) { config in
                        if let config = config {
                            selectedShip = ships.first { $0.ship_type_id == config.shipTypeId }
                        }
                    }

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
                        }
                        .padding(.top, 8)
                    }
                }

                Section(header: Text("Skills")) {
                    HStack {
                        Text("Advanced Spaceship Command")
                        Spacer()
                        Stepper(
                            value: Binding(
                                get: { selectedConfig?.skills["advanced_spaceship_command"] ?? 0 },
                                set: {
                                    if selectedConfig != nil {
                                        selectedConfig?.skills["advanced_spaceship_command"] = $0
                                    }
                                }
                            ),
                            in: 0...5
                        )
                        Text("\(selectedConfig?.skills["advanced_spaceship_command"] ?? 0)")
                            .frame(minWidth: 20)
                    }
                }

                Section(header: Text("Route Planning")) {
                    TextField("Origin System ID", text: $originText)
                        .keyboardType(.numberPad)
                    TextField("Destination System ID", text: $destinationText)
                        .keyboardType(.numberPad)

                    Button(action: planJumpChain) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            }
                            Text("Plan Jump Chain")
                                .frame(maxWidth: .infinity, alignment: .center)
                        }
                    }
                    .disabled(isLoading || selectedShip == nil)
                }

                if let error = errorMessage {
                    Section(header: Text("Error")) {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }

                if let chain = plannedChain {
                    JumpChainResultView(chain: chain)
                }
            }
            .navigationTitle("Capital Jump Planner")
            .onAppear(perform: loadShips)
        }
    }

    private func loadShips() {
        client.getCapitalShips()
            .receive(on: DispatchQueue.main)
            .sink { _ in } receiveValue: { ships in
                self.ships = ships
            }
            .store(in: &client.cancellables)
    }

    private func planJumpChain() {
        guard let ship = selectedShip,
              let origin = Int(originText),
              let destination = Int(destinationText) else {
            errorMessage = "Invalid input"
            return
        }

        isLoading = true
        errorMessage = nil

        let skills = selectedConfig?.skills ?? [:]
        client.planJumpChain(
            origin: origin,
            destination: destination,
            shipTypeId: ship.ship_type_id,
            skills: skills
        )
        .receive(on: DispatchQueue.main)
        .sink { completion in
            isLoading = false
            if case .failure(let error) = completion {
                errorMessage = error.localizedDescription
            }
        } receiveValue: { chain in
            self.plannedChain = chain
        }
        .store(in: &client.cancellables)
    }
}

struct JumpChainResultView: View {
    let chain: JumpChain

    var body: some View {
        Section(header: Text("Jump Route Result")) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Total Jumps")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text("\(chain.total_jumps)")
                            .font(.headline)
                    }
                    Spacer()
                    VStack(alignment: .leading) {
                        Text("Distance")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text(String(format: "%.2f LY", chain.total_distance_ly))
                            .font(.headline)
                    }
                    Spacer()
                    VStack(alignment: .leading) {
                        Text("Fuel")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text(String(format: "%.0f", chain.total_fuel_consumed))
                            .font(.headline)
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(8)

                if chain.requires_refuel {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.orange)
                        Text("Refueling required")
                            .font(.caption)
                    }
                }

                Text("Jump Route")
                    .font(.headline)

                ForEach(Array(chain.legs.enumerated()), id: \.offset) { index, leg in
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Jump \(index + 1)")
                            .font(.caption)
                            .foregroundColor(.gray)
                        HStack {
                            VStack(alignment: .leading) {
                                Text(leg.origin_name)
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                Text("↓")
                                    .font(.caption2)
                                Text(leg.destination_name)
                                    .font(.caption)
                                    .fontWeight(.semibold)
                            }
                            Spacer()
                            VStack(alignment: .trailing, spacing: 2) {
                                Text(String(format: "%.2f LY", leg.distance_ly))
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                Text(String(format: "%.0f fuel", leg.fuel_consumed))
                                    .font(.caption)
                                    .foregroundColor(.orange)
                            }
                        }
                    }
                    .padding(.vertical, 6)
                }
            }
        }
    }
}

// MARK: - Settings Tab

struct SettingsTab: View {
    @EnvironmentObject var appState: AppState
    @State private var editingURL = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("API Configuration")) {
                    HStack {
                        Text("API URL")
                        Spacer()
                        Text(appState.apiURL)
                            .font(.caption)
                            .foregroundColor(.blue)
                    }

                    Button(action: { editingURL = true }) {
                        Text("Edit API URL")
                    }
                }

                Section(header: Text("About")) {
                    DetailRow(label: "App Version", value: "1.0.0")
                    DetailRow(label: "Build", value: "Phase 3")
                    HStack {
                        Text("EVE Online")
                        Spacer()
                        Link("Official Site", destination: URL(string: "https://www.eveonline.com")!)
                            .font(.caption)
                    }
                }

                Section(header: Text("Documentation")) {
                    Link("API Documentation", destination: URL(string: "\(appState.apiURL)/docs")!)
                    Link("ESI Reference", destination: URL(string: "https://esi.eveonline.com/docs")!)
                    Link("Privacy Policy", destination: URL(string: "https://example.com/privacy")!)
                }
            }
            .navigationTitle("Settings")
            .sheet(isPresented: $editingURL) {
                EditAPIURLView(apiURL: $appState.apiURL, isPresented: $editingURL)
            }
        }
    }
}

struct EditAPIURLView: View {
    @Binding var apiURL: String
    @Binding var isPresented: Bool
    @State private var tempURL: String = ""

    var body: some View {
        NavigationView {
            Form {
                TextField("API URL", text: $tempURL)
                    .keyboardType(.URL)
            }
            .navigationTitle("Edit API URL")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { isPresented = false }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        if !tempURL.isEmpty {
                            apiURL = tempURL
                        }
                        isPresented = false
                    }
                }
            }
            .onAppear {
                tempURL = apiURL
            }
        }
    }
}

// MARK: - Helper Views

struct SecurityBadge: View {
    let secClass: String

    var body: some View {
        Text(secClass.uppercased())
            .font(.caption2)
            .fontWeight(.semibold)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(securityColor)
            .foregroundColor(.white)
            .cornerRadius(4)
    }

    private var securityColor: Color {
        switch secClass.lowercased() {
        case "high_sec": return .blue
        case "low_sec": return .orange
        case "null_sec": return .red
        case "wormhole": return .purple
        default: return .gray
        }
    }
}

struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.gray)
            Spacer()
            Text(value)
                .fontWeight(.semibold)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct EVEMapApp_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AppState())
    }
}
#endif
