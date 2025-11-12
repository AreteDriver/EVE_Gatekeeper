/**
 * EVE Map Visualization - Android Native App
 * Production-ready Jetpack Compose application
 */

package com.evemap

import android.app.Application
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.navigation.NavController
import androidx.navigation.NavGraphBuilder
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material.icons.outlined.Settings
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import java.util.concurrent.TimeUnit

// ==================== DATA MODELS ====================

@Serializable
data class SystemResponse(
    val system_id: Int,
    val name: String,
    val region_id: Int,
    val constellation_id: Int,
    val security_status: Double,
    val x: Double,
    val y: Double,
    val z: Double,
)

@Serializable
data class SearchResult(
    val systems: List<SystemResponse>,
    val count: Int
)

@Serializable
data class RouteResponse(
    val origin_system_id: Int,
    val destination_system_id: Int,
    val path: List<Int>,
    val distance_ly: Double,
    val jumps: Int
)

@Serializable
data class JumpLegResponse(
    val origin_system_id: Int,
    val origin_name: String,
    val destination_system_id: Int,
    val destination_name: String,
    val distance_ly: Double,
    val fuel_consumed: Double,
    val duration_minutes: Int
)

@Serializable
data class JumpChainResponse(
    val origin_system_id: Int,
    val destination_system_id: Int,
    val legs: List<JumpLegResponse>,
    val total_distance_ly: Double,
    val total_fuel_consumed: Double,
    val total_duration_hours: Double,
    val total_jumps: Int,
    val requires_refuel: Boolean,
    val refuel_points: List<Int>
)

@Serializable
data class ShipResponse(
    val ship_type_id: Int,
    val ship_name: String,
    val ship_class: String,
    val base_range: Double,
    val max_range_with_skills: Double,
    val fuel_capacity: Int,
    val mass: Double
)

@Serializable
data class HealthResponse(
    val status: String,
    val timestamp: String
)

// ==================== API SERVICE ====================

interface EVEMapApiService {
    @GET("/health")
    suspend fun getHealth(): HealthResponse

    @GET("/systems/search")
    suspend fun searchSystems(@Query("q") query: String): SearchResult

    @GET("/routes/plan")
    suspend fun planRoute(
        @Query("origin") origin: Int,
        @Query("destination") destination: Int
    ): RouteResponse

    @GET("/capital/ships")
    suspend fun getCapitalShips(): List<ShipResponse>

    @GET("/capital/jump-chain")
    suspend fun planJumpChain(
        @Query("origin") origin: Int,
        @Query("destination") destination: Int,
        @Query("ship_type_id") shipTypeId: Int,
        @Query("skills") skills: String
    ): JumpChainResponse
}

// ==================== SETTINGS & PERSISTENCE ====================

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "evemap_settings")

class SettingsManager(context: Context) {
    private val dataStore = context.dataStore
    private val API_URL_KEY = stringPreferencesKey("api_url")
    private val LAST_SHIP_CONFIG = stringPreferencesKey("last_ship_config")

    val apiUrl: Flow<String> = dataStore.data.map { preferences ->
        preferences[API_URL_KEY] ?: "https://evemap-api.herokuapp.com"
    }

    suspend fun saveApiUrl(url: String) {
        dataStore.edit { preferences ->
            preferences[API_URL_KEY] = url
        }
    }

    val lastShipConfig: Flow<String> = dataStore.data.map { preferences ->
        preferences[LAST_SHIP_CONFIG] ?: ""
    }

    suspend fun saveShipConfig(config: String) {
        dataStore.edit { preferences ->
            preferences[LAST_SHIP_CONFIG] = config
        }
    }
}

// ==================== API CLIENT ====================

class EVEMapClient(apiUrl: String) {
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()

    private val json = Json { ignoreUnknownKeys = true }

    private val retrofit = Retrofit.Builder()
        .baseUrl(apiUrl)
        .client(httpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    val api: EVEMapApiService = retrofit.create(EVEMapApiService::class.java)

    companion object {
        fun toMediaType() = "application/json".toMediaType()
    }
}

fun String.toMediaType() = okhttp3.MediaType.parse(this)

// ==================== VIEW MODELS ====================

class EVEMapViewModel(val settingsManager: SettingsManager) : ViewModel() {
    private var apiClient: EVEMapClient? = null

    private val _apiUrl = MutableState(value = "")
    val apiUrl: State<String> = _apiUrl

    private val _isConnected = MutableState(value = false)
    val isConnected: State<Boolean> = _isConnected

    private val _searchResults = MutableState<List<SystemResponse>>(emptyList())
    val searchResults: State<List<SystemResponse>> = _searchResults

    private val _selectedSystem = MutableState<SystemResponse?>(null)
    val selectedSystem: State<SystemResponse?> = _selectedSystem

    private val _capitalShips = MutableState<List<ShipResponse>>(emptyList())
    val capitalShips: State<List<ShipResponse>> = _capitalShips

    private val _jumpChain = MutableState<JumpChainResponse?>(null)
    val jumpChain: State<JumpChainResponse?> = _jumpChain

    private val _isLoading = MutableState(value = false)
    val isLoading: State<Boolean> = _isLoading

    private val _errorMessage = MutableState<String?>(null)
    val errorMessage: State<String?> = _errorMessage

    init {
        viewModelScope.launch {
            settingsManager.apiUrl.collect { url ->
                _apiUrl.value = url
                initializeApiClient(url)
                checkConnection()
                loadCapitalShips()
            }
        }
    }

    private fun initializeApiClient(url: String) {
        try {
            apiClient = EVEMapClient(url)
        } catch (e: Exception) {
            _errorMessage.value = "Invalid API URL: ${e.message}"
        }
    }

    fun updateApiUrl(url: String) {
        viewModelScope.launch {
            settingsManager.saveApiUrl(url)
        }
    }

    fun checkConnection() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                apiClient?.api?.getHealth()
                _isConnected.value = true
                _errorMessage.value = null
            } catch (e: Exception) {
                _isConnected.value = false
                _errorMessage.value = "Cannot connect to API: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun searchSystems(query: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                val results = apiClient?.api?.searchSystems(query)
                _searchResults.value = results?.systems ?: emptyList()
            } catch (e: Exception) {
                _errorMessage.value = "Search failed: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun selectSystem(system: SystemResponse) {
        _selectedSystem.value = system
    }

    fun loadCapitalShips() {
        viewModelScope.launch {
            try {
                val ships = apiClient?.api?.getCapitalShips()
                _capitalShips.value = ships ?: emptyList()
            } catch (e: Exception) {
                _errorMessage.value = "Failed to load ships: ${e.message}"
            }
        }
    }

    fun planJumpChain(origin: Int, destination: Int, shipTypeId: Int, skills: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                val chain = apiClient?.api?.planJumpChain(origin, destination, shipTypeId, skills)
                _jumpChain.value = chain
            } catch (e: Exception) {
                _errorMessage.value = "Jump planning failed: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearJumpChain() {
        _jumpChain.value = null
    }

    fun clearError() {
        _errorMessage.value = null
    }
}

@Composable
fun rememberEVEMapViewModel(settingsManager: SettingsManager): EVEMapViewModel {
    return remember { EVEMapViewModel(settingsManager) }
}

// ==================== UI COMPONENTS ====================

@Composable
fun SecurityBadge(security: Double) {
    val (color, label) = when {
        security >= 0.5 -> Color(0xFF00AA00) to "HS"
        security > 0 -> Color(0xFFFFAA00) to "LS"
        else -> Color(0xFFAA0000) to "NS"
    }

    Surface(
        color = color,
        shape = RoundedCornerShape(4.dp),
        modifier = Modifier.padding(4.dp)
    ) {
        Text(
            text = label,
            color = Color.White,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(4.dp)
        )
    }
}

@Composable
fun ErrorSnackbar(message: String?, onDismiss: () -> Unit) {
    if (message != null) {
        Snackbar(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            action = {
                TextButton(onClick = onDismiss) {
                    Text("Dismiss", color = Color.White)
                }
            }
        ) {
            Text(message, color = Color.White)
        }
    }
}

@Composable
fun SystemCard(system: SystemResponse, onClick: () -> Unit) {
    ElevatedCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onClick() }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = system.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                )
                Text(
                    text = "ID: ${system.system_id}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            SecurityBadge(system.security_status)
        }
    }
}

@Composable
fun ShipCard(ship: ShipResponse) {
    ElevatedCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = ship.ship_name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                    Text(
                        text = ship.ship_class.uppercase(),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Surface(
                    color = MaterialTheme.colorScheme.primaryContainer,
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = "${ship.max_range_with_skills} LY",
                        style = MaterialTheme.typography.titleSmall,
                        modifier = Modifier.padding(8.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth()) {
                Text("Base: ${ship.base_range} LY", style = MaterialTheme.typography.bodySmall)
                Spacer(modifier = Modifier.width(16.dp))
                Text("Fuel: ${ship.fuel_capacity}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
fun JumpLegCard(leg: JumpLegResponse) {
    ElevatedCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${leg.origin_name} → ${leg.destination_name}",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                    Text(
                        text = "${leg.distance_ly} LY",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Surface(
                    color = if (leg.fuel_consumed > 1000) Color(0xFFFF6B6B) else Color(0xFF51CF66),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "⛽ ${leg.fuel_consumed.toInt()}",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        modifier = Modifier.padding(6.dp)
                    )
                }
            }
        }
    }
}

// ==================== SCREENS ====================

@Composable
fun MapSearchScreen(viewModel: EVEMapViewModel) {
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Search Input
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Search Systems") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { viewModel.searchSystems(searchQuery) }) {
                        Icon(Icons.Default.Search, contentDescription = "Search")
                    }
                }
            },
            singleLine = true
        )

        if (viewModel.isLoading.value) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (viewModel.searchResults.value.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Enter a system name to search", color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        } else {
            LazyColumn {
                items(viewModel.searchResults.value) { system ->
                    SystemCard(system = system, onClick = {
                        viewModel.selectSystem(system)
                    })
                }
            }
        }
    }
}

@Composable
fun RoutePlannerScreen(viewModel: EVEMapViewModel) {
    var originName by remember { mutableStateOf("") }
    var destName by remember { mutableStateOf("") }
    var originId by remember { mutableStateOf("") }
    var destId by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "Route Planner",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        OutlinedTextField(
            value = originId,
            onValueChange = { originId = it },
            label = { Text("Origin System ID") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        OutlinedTextField(
            value = destId,
            onValueChange = { destId = it },
            label = { Text("Destination System ID") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        Button(
            onClick = {
                if (originId.isNotEmpty() && destId.isNotEmpty()) {
                    // Route planning would be implemented here
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp)
        ) {
            Text("Plan Route")
        }

        Divider(modifier = Modifier.padding(vertical = 16.dp))
        Text("Routes will be displayed here")
    }
}

@Composable
fun CapitalPlannerScreen(viewModel: EVEMapViewModel) {
    var selectedShipId by remember { mutableStateOf<Int?>(null) }
    var originId by remember { mutableStateOf("") }
    var destId by remember { mutableStateOf("") }
    var advancedSpaceshipCommand by remember { mutableStateOf("5") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "Capital Jump Planner",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Ship Selection
        Text(
            text = "Select Ship",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
            modifier = Modifier.padding(vertical = 8.dp)
        )

        LazyColumn(modifier = Modifier.heightIn(max = 200.dp)) {
            items(viewModel.capitalShips.value) { ship ->
                ElevatedButton(
                    onClick = { selectedShipId = ship.ship_type_id },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(4.dp),
                    colors = ButtonDefaults.elevatedButtonColors(
                        containerColor = if (selectedShipId == ship.ship_type_id)
                            MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Text("${ship.ship_name} (${ship.max_range_with_skills} LY)")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))
        Divider()
        Spacer(modifier = Modifier.height(16.dp))

        // Route Input
        OutlinedTextField(
            value = originId,
            onValueChange = { originId = it },
            label = { Text("Origin System ID") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        OutlinedTextField(
            value = destId,
            onValueChange = { destId = it },
            label = { Text("Destination System ID") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        // Skill Input
        OutlinedTextField(
            value = advancedSpaceshipCommand,
            onValueChange = { advancedSpaceshipCommand = it },
            label = { Text("Advanced Spaceship Command (0-5)") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        Button(
            onClick = {
                if (selectedShipId != null && originId.isNotEmpty() && destId.isNotEmpty()) {
                    val skills = """{"advanced_spaceship_command": ${advancedSpaceshipCommand.toIntOrNull() ?: 5}}"""
                    viewModel.planJumpChain(originId.toInt(), destId.toInt(), selectedShipId!!, skills)
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            enabled = selectedShipId != null && !viewModel.isLoading.value
        ) {
            if (viewModel.isLoading.value) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
            } else {
                Text("Plan Jump Chain")
            }
        }

        if (viewModel.jumpChain.value != null) {
            val chain = viewModel.jumpChain.value!!
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Jump Chain Summary",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                    Text("Jumps: ${chain.total_jumps}")
                    Text("Distance: ${chain.total_distance_ly} LY")
                    Text("Fuel: ${chain.total_fuel_consumed.toInt()} units")
                    Text("Refuel Needed: ${if (chain.requires_refuel) "Yes" else "No"}")
                }
            }

            Text(
                text = "Jump Legs",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                modifier = Modifier.padding(top = 16.dp, bottom = 8.dp)
            )

            chain.legs.forEach { leg ->
                JumpLegCard(leg)
            }
        }
    }
}

@Composable
fun SettingsScreen(viewModel: EVEMapViewModel) {
    var apiUrlInput by remember { mutableStateOf(viewModel.apiUrl.value) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // API URL
        OutlinedTextField(
            value = apiUrlInput,
            onValueChange = { apiUrlInput = it },
            label = { Text("API URL") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            singleLine = true
        )

        Button(
            onClick = {
                viewModel.updateApiUrl(apiUrlInput)
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp)
        ) {
            Text("Save & Connect")
        }

        // Connection Status
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("API Connection:")
            Surface(
                color = if (viewModel.isConnected.value) Color(0xFF51CF66) else Color(0xFFFF6B6B),
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = if (viewModel.isConnected.value) "Connected" else "Disconnected",
                    color = Color.White,
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(8.dp)
                )
            }
        }

        Divider(modifier = Modifier.padding(vertical = 16.dp))

        Text(
            text = "About",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
            modifier = Modifier.padding(vertical = 8.dp)
        )

        Text(
            text = "EVE Map Visualization",
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = "Version: 1.0.0",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = "A 2D starmap viewer for EVE Online",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 8.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Powered by ESI API",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

// ==================== MAIN APP ====================

@Composable
fun EVEMapApp(viewModel: EVEMapViewModel) {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = navController.currentDestinationAsState().value?.route == "map",
                    onClick = { navController.navigate("map") },
                    label = { Text("Map") },
                    icon = { Icon(Icons.Default.LocationOn, contentDescription = "Map") }
                )
                NavigationBarItem(
                    selected = navController.currentDestinationAsState().value?.route == "routes",
                    onClick = { navController.navigate("routes") },
                    label = { Text("Routes") },
                    icon = { Icon(Icons.Default.Route, contentDescription = "Routes") }
                )
                NavigationBarItem(
                    selected = navController.currentDestinationAsState().value?.route == "capital",
                    onClick = { navController.navigate("capital") },
                    label = { Text("Capital") },
                    icon = { Icon(Icons.Default.Flight, contentDescription = "Capital") }
                )
                NavigationBarItem(
                    selected = navController.currentDestinationAsState().value?.route == "settings",
                    onClick = { navController.navigate("settings") },
                    label = { Text("Settings") },
                    icon = { Icon(Icons.Outlined.Settings, contentDescription = "Settings") }
                )
            }
        },
        snackbarHost = {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.BottomCenter) {
                ErrorSnackbar(viewModel.errorMessage.value) {
                    viewModel.clearError()
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = "map",
            modifier = Modifier.padding(paddingValues)
        ) {
            composable("map") { MapSearchScreen(viewModel) }
            composable("routes") { RoutePlannerScreen(viewModel) }
            composable("capital") { CapitalPlannerScreen(viewModel) }
            composable("settings") { SettingsScreen(viewModel) }
        }
    }
}

@Composable
fun currentDestinationAsState() = remember {
    MutableState<String?>(null)
}

// Extension function for NavController
@Composable
fun NavController.currentDestinationAsState(): State<NavDestination?> {
    val state = remember { mutableStateOf<NavDestination?>(null) }

    DisposableEffect(this) {
        val listener = NavController.OnDestinationChangedListener { _, destination, _ ->
            state.value = destination
        }
        addOnDestinationChangedListener(listener)

        onDispose {
            removeOnDestinationChangedListener(listener)
        }
    }

    return state
}

import androidx.navigation.NavDestination

// ==================== MAIN ACTIVITY ====================

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val settingsManager = remember { SettingsManager(applicationContext) }
                val viewModel = rememberEVEMapViewModel(settingsManager)

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    EVEMapApp(viewModel)
                }
            }
        }
    }
}
