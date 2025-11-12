// iOS Swift Example: EVE Map API Client
// This demonstrates how to build an iOS app consuming the EVE Map REST API

import Foundation
import Combine

// MARK: - API Models

struct System: Codable, Identifiable {
    let id: Int
    let name: String
    let region_id: Int
    let constellation_id: Int
    let security: Float
    let sec_class: String
    let is_wormhole: Bool
    let x: Float?
    let y: Float?
    let z: Float?
    let planets: Int
    let stars: Int
    let stargates: Int
}

struct Region: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?
}

struct RouteResponse: Codable {
    let route: [Int]
    let jumps: Int
    let systems: [String]
    let security_profile: String
}

struct HeatmapData: Codable {
    let kills: [String: Float]
    let jumps: [String: Float]
    let timestamp: String
}

struct IntelLayers: Codable {
    let timestamp: String
    let activity: HeatmapData
    let incursions: [Incursion]
    let sovereignty: [String: SovereigntyData]
    let campaigns: [Campaign]
}

struct Incursion: Codable, Identifiable {
    let id: String
    let state: String
    let type: String
    let faction: Int?
    let influence: Float
    let staging_system: Int?
    let systems: [Int]
    let has_boss: Bool
}

struct SovereigntyData: Codable {
    let alliance_id: Int?
    let faction_id: Int?
    let corporation_id: Int?
}

struct Campaign: Codable, Identifiable {
    let id: String
    let type: String
    let system_id: Int
    let constellation_id: Int
    let region_id: Int
    let defending_id: Int?
    let attacking_id: Int?
    let start_time: String?
    let contested: Bool
}

// MARK: - API Client

class EVEMapClient: ObservableObject {
    private let baseURL = URL(string: "http://localhost:8000")!
    private var cancellables = Set<AnyCancellable>()

    @Published var isLoading = false
    @Published var errorMessage: String? = nil

    // MARK: - Search & System Queries

    func searchSystems(query: String) -> AnyPublisher<[System], Error> {
        let urlComponents = URLComponents(
            url: baseURL.appendingPathComponent("systems/search"),
            resolvingAgainstBaseURL: true
        )!

        var components = urlComponents
        components.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "limit", value: "10")
        ]

        return URLSession.shared.dataTaskPublisher(for: components.url!)
            .map { $0.data }
            .decode(type: [System].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func getSystem(id: Int) -> AnyPublisher<System, Error> {
        let url = baseURL.appendingPathComponent("systems/\(id)")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: System.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func getSystemNeighbors(id: Int) -> AnyPublisher<[System], Error> {
        let url = baseURL.appendingPathComponent("systems/\(id)/neighbors")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: [System].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    // MARK: - Region Queries

    func listRegions() -> AnyPublisher<[Region], Error> {
        let url = baseURL.appendingPathComponent("regions")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: [Region].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func getRegion(id: Int) -> AnyPublisher<Region, Error> {
        let url = baseURL.appendingPathComponent("regions/\(id)")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: Region.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    // MARK: - Route Planning

    func planRoute(
        origin: Int,
        destination: Int,
        avoidLowsec: Bool = false,
        avoidNullsec: Bool = false
    ) -> AnyPublisher<RouteResponse, Error> {
        let url = baseURL.appendingPathComponent("routes/plan")

        let requestBody: [String: Any] = [
            "origin": origin,
            "destination": destination,
            "avoid_lowsec": avoidLowsec,
            "avoid_nullsec": avoidNullsec,
            "avoid_systems": [],
            "avoid_regions": []
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: requestBody)

        return URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .decode(type: RouteResponse.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    // MARK: - Analysis

    func getHubSystems(limit: Int = 20) -> AnyPublisher<[SystemHub], Error> {
        var components = URLComponents(
            url: baseURL.appendingPathComponent("analysis/hubs"),
            resolvingAgainstBaseURL: true
        )!
        components.queryItems = [URLQueryItem(name: "limit", value: "\(limit)")]

        return URLSession.shared.dataTaskPublisher(for: components.url!)
            .map { $0.data }
            .decode(type: HubsResponse.self, decoder: JSONDecoder())
            .map { $0.hubs }
            .eraseToAnyPublisher()
    }

    // MARK: - Live Intel

    func getActivityHeatmap() -> AnyPublisher<HeatmapData, Error> {
        let url = baseURL.appendingPathComponent("intel/activity")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: HeatmapData.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func getAllIntel() -> AnyPublisher<IntelLayers, Error> {
        let url = baseURL.appendingPathComponent("intel/all")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: IntelLayers.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }

    func getIncursions() -> AnyPublisher<[Incursion], Error> {
        let url = baseURL.appendingPathComponent("intel/incursions")
        return URLSession.shared.dataTaskPublisher(for: url)
            .map { $0.data }
            .decode(type: IncursionsResponse.self, decoder: JSONDecoder())
            .map { $0.incursions }
            .eraseToAnyPublisher()
    }

    // MARK: - Offline Data

    func downloadGraph() -> AnyPublisher<URL, Error> {
        let url = baseURL.appendingPathComponent("static/universe_graph.json")
        let documentsDirectory = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        )[0]
        let fileURL = documentsDirectory.appendingPathComponent("universe_graph.json")

        return URLSession.shared.downloadTaskPublisher(for: url)
            .tryMap { (tempURL, response) in
                try FileManager.default.moveItem(at: tempURL, to: fileURL)
                return fileURL
            }
            .eraseToAnyPublisher()
    }
}

// Helper structures
struct HubsResponse: Codable {
    let hubs: [SystemHub]
}

struct SystemHub: Codable, Identifiable {
    let id: Int
    let name: String
    let connections: Int
}

struct IncursionsResponse: Codable {
    let incursions: [Incursion]
}

// MARK: - SwiftUI Example View

import SwiftUI

struct EVEMapView: View {
    @StateObject private var client = EVEMapClient()
    @State private var searchText = ""
    @State private var searchResults: [System] = []
    @State private var selectedSystem: System?
    @State private var routeFrom: Int?
    @State private var routeTo: Int?
    @State private var plannedRoute: RouteResponse?

    var body: some View {
        NavigationView {
            VStack {
                // Search Bar
                SearchBar(text: $searchText, onSearch: searchSystems)

                // Search Results
                if !searchResults.isEmpty {
                    List(searchResults) { system in
                        VStack(alignment: .leading) {
                            Text(system.name)
                                .font(.headline)
                            HStack {
                                Text("Security: \(String(format: "%.1f", system.security))")
                                    .font(.caption)
                                Spacer()
                                Text(system.sec_class)
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(securityColor(system.sec_class))
                                    .cornerRadius(4)
                            }
                        }
                        .onTapGesture {
                            selectedSystem = system
                        }
                    }
                } else {
                    VStack {
                        Text("Search for systems...")
                            .foregroundColor(.gray)
                        Text("e.g., 'Jita', 'Perimeter', 'Amarr'")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                }
            }
            .navigationTitle("EVE Map")
            .sheet(item: $selectedSystem) { system in
                SystemDetailView(system: system, client: client)
            }
        }
    }

    private func searchSystems() {
        guard !searchText.isEmpty else {
            searchResults = []
            return
        }

        client.searchSystems(query: searchText)
            .receive(on: DispatchQueue.main)
            .sink { completion in
                if case .failure(let error) = completion {
                    client.errorMessage = error.localizedDescription
                }
            } receiveValue: { systems in
                self.searchResults = systems
            }
            .store(in: &client.cancellables)
    }

    private func securityColor(_ secClass: String) -> Color {
        switch secClass {
        case "high_sec":
            return .blue
        case "low_sec":
            return .orange
        case "null_sec":
            return .red
        case "wormhole":
            return .purple
        default:
            return .gray
        }
    }
}

struct SystemDetailView: View {
    let system: System
    let client: EVEMapClient
    @State private var neighbors: [System] = []
    @Environment(\.presentationMode) var presentationMode

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 16) {
                Text(system.name)
                    .font(.title)

                VStack(alignment: .leading, spacing: 8) {
                    DetailRow(label: "Region ID", value: "\(system.region_id)")
                    DetailRow(label: "Security", value: String(format: "%.1f", system.security))
                    DetailRow(label: "Class", value: system.sec_class)
                    DetailRow(label: "Planets", value: "\(system.planets)")
                    DetailRow(label: "Stargates", value: "\(system.stargates)")
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(8)

                if !neighbors.isEmpty {
                    Text("Adjacent Systems")
                        .font(.headline)
                    List(neighbors) { neighbor in
                        Text(neighbor.name)
                    }
                }

                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
            .onAppear(perform: loadNeighbors)
        }
    }

    private func loadNeighbors() {
        client.getSystemNeighbors(id: system.id)
            .receive(on: DispatchQueue.main)
            .sink { _ in
            } receiveValue: { neighbors in
                self.neighbors = neighbors
            }
            .store(in: &client.cancellables)
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

struct SearchBar: View {
    @Binding var text: String
    var onSearch: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)

            TextField("Search systems...", text: $text)
                .onSubmit(onSearch)

            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
        .cornerRadius(8)
        .padding()
    }
}

#if DEBUG
struct EVEMapView_Previews: PreviewProvider {
    static var previews: some View {
        EVEMapView()
    }
}
#endif
