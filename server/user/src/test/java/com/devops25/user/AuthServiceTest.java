package com.devops25.user;

import com.devops25.user.config.JwtService;
import com.devops25.user.dto.AuthRequest;
import com.devops25.user.dto.AuthResponse;
import com.devops25.user.exceptions.InvalidRequestException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
    @Mock
    private UserRepository repository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    @Mock
    private AuthenticationManager authenticationManager;

    @InjectMocks
    private AuthService authService;

    @Test
    void register_NewUser_Success() {
        AuthRequest request = new AuthRequest("testuser", "password", "Test University");
        when(repository.findByUsername("testuser")).thenReturn(Optional.empty());
        when(passwordEncoder.encode("password")).thenReturn("encodedPassword");

        AuthResponse response = authService.register(request);

        assertEquals("Registration successful", response.getMessage());
        assertEquals("testuser", response.getUsername());
        verify(repository, times(1)).save(any(com.devops25.user.User.class));
    }

    @Test
    void register_ExistingUser_ReturnsUsernameExists() {
        AuthRequest request = new AuthRequest("existinguser", "password", null);
        when(repository.findByUsername("existinguser")).thenReturn(Optional.of(new com.devops25.user.User()));

        AuthResponse response = authService.register(request);

        assertEquals("Username already exists", response.getMessage());
        verify(repository, never()).save(any(com.devops25.user.User.class));
    }

    @Test
    void register_MissingUsernameOrPassword_ThrowsException() {
        assertThrows(InvalidRequestException.class, () -> {
            authService.register(new AuthRequest(null, "password", null));
        });

        assertThrows(InvalidRequestException.class, () -> {
            authService.register(new AuthRequest("user", null, null));
        });
    }

    @Test
    void authenticate_ValidCredentials_ReturnsSuccess() {
        AuthRequest request = new AuthRequest("validuser", "correctpass", null);

        // Create domain user that implements UserDetails
        com.devops25.user.User user = com.devops25.user.User.builder()
                .username("validuser")
                .password("encodedPass")
                .build();

        // Mock authentication
        Authentication authentication = mock(Authentication.class);
        when(authentication.getPrincipal()).thenReturn(user);

        when(authenticationManager.authenticate(any()))
                .thenReturn(authentication);

        when(jwtService.generateToken(user)).thenReturn("generatedToken");

        AuthResponse response = authService.authenticate(request);

        assertEquals("Login successful", response.getMessage());
        assertEquals("validuser", response.getUsername());
        assertEquals("generatedToken", response.getToken());
    }

    @Test
    void authenticate_InvalidCredentials_ThrowsException() {
        AuthRequest request = new AuthRequest("invaliduser", "wrongpass", null);

        when(authenticationManager.authenticate(any()))
                .thenThrow(new BadCredentialsException("Invalid credentials"));

        assertThrows(BadCredentialsException.class, () -> {
            authService.authenticate(request);
        });
    }
}