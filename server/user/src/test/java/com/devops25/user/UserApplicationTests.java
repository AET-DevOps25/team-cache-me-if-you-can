package com.devops25.user;

import com.devops25.user.config.CustomLogoutHandler;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

@SpringBootTest
@ActiveProfiles("test")
@Testcontainers  // Add this annotation
class UserApplicationTests {

	// Start MySQL container
	@Container
	static final MySQLContainer<?> mysqlContainer = new MySQLContainer<>("mysql:8.0.32")
			.withDatabaseName("testdb")
			.withUsername("test")
			.withPassword("test");

	// Dynamically override properties
	@DynamicPropertySource
	static void registerProperties(DynamicPropertyRegistry registry) {
		registry.add("spring.datasource.url", mysqlContainer::getJdbcUrl);
		registry.add("spring.datasource.username", mysqlContainer::getUsername);
		registry.add("spring.datasource.password", mysqlContainer::getPassword);
	}

	@MockitoBean
	private UserRepository userRepository;

	@MockitoBean
	private TokenBlacklistService tokenBlacklistService;

	@MockitoBean
	private PasswordEncoder passwordEncoder;

	@MockitoBean
	private CustomLogoutHandler customLogoutHandler;

	@Test
	void contextLoads() {
		// Test passes if application context loads
		// Container starts automatically before tests
	}
}