package com.devops25.user;

import com.devops25.user.config.JwtService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class JwtServiceTest {

    private JwtService jwtService;

    @Mock
    private TokenBlacklistService tokenBlacklistService;

    private UserDetails userDetails;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService(tokenBlacklistService);
        userDetails = User.builder()
                .username("testuser")
                .password("password")
                .authorities(() -> "ROLE_USER")
                .build();
    }

    @Test
    void generateToken_ValidUser_ReturnsToken() {
        String token = jwtService.generateToken(userDetails);
        assertNotNull(token);
        assertTrue(token.length() > 100); // Tokens are long strings
    }

    @Test
    void extractUsername_ValidToken_ReturnsUsername() {
        String token = jwtService.generateToken(userDetails);
        String username = jwtService.extractUsername(token);
        assertEquals("testuser", username);
    }

    @Test
    void isTokenValid_ValidToken_ReturnsTrue() {
        String token = jwtService.generateToken(userDetails);
        when(tokenBlacklistService.isTokenBlacklisted(token)).thenReturn(false);
        assertTrue(jwtService.isTokenValid(token, userDetails));
    }

    @Test
    void isTokenValid_BlacklistedToken_ReturnsFalse() {
        String token = jwtService.generateToken(userDetails);
        when(tokenBlacklistService.isTokenBlacklisted(token)).thenReturn(true);
        assertFalse(jwtService.isTokenValid(token, userDetails));
    }
}