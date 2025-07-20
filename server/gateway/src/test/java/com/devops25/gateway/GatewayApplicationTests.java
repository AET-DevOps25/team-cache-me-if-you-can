package com.devops25.gateway;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.security.Key;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.*;

class GatewayServiceTest {

    private JwtService jwtService;
    private String testSecret = "dGVzdC1zZWNyZXQtZm9yLWp3dC10ZXN0aW5nLXRoaXMtaXMtYS12ZXJ5LWxvbmctc2VjcmV0LWtleQ==";
    private Key testKey;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService();
        ReflectionTestUtils.setField(jwtService, "SECRET_KEY", testSecret);
        testKey = Keys.hmacShaKeyFor(java.util.Base64.getDecoder().decode(testSecret));
    }

    @Test
    void extractUsername_ShouldReturnCorrectUsername() {
        String token = createTestToken("testuser", new Date(System.currentTimeMillis() + 1000 * 60 * 60));

        String extractedUsername = jwtService.extractUsername(token);

        assertEquals("testuser", extractedUsername);
    }

    @Test
    void isTokenValid_ShouldReturnTrueForValidToken() {
        String token = createTestToken("testuser", new Date(System.currentTimeMillis() + 1000 * 60 * 60));

        boolean isValid = jwtService.isTokenValid(token);

        assertTrue(isValid);
    }

    @Test
    void isTokenValid_ShouldReturnFalseForExpiredToken() {
        String token = createTestToken("testuser", new Date(System.currentTimeMillis() - 1000));

        boolean isValid = jwtService.isTokenValid(token);

        assertFalse(isValid);
    }

    @Test
    void isTokenValid_ShouldReturnFalseForInvalidToken() {
        String invalidToken = "invalid.jwt.token";

        boolean isValid = jwtService.isTokenValid(invalidToken);

        assertFalse(isValid);
    }

    private String createTestToken(String username, Date expiration) {
        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(new Date())
                .setExpiration(expiration)
                .signWith(testKey, SignatureAlgorithm.HS256)
                .compact();
    }
}