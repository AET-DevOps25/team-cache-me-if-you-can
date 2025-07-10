package com.devops25.user;

import com.devops25.user.dto.AuthRequest;
import com.devops25.user.dto.AuthResponse;
import com.devops25.user.exceptions.InvalidRequestException;
import com.devops25.user.exceptions.UsernameTakenException; // NEW Import
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    private final AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody @Valid AuthRequest request) {
        try {
            AuthResponse response = authService.register(request);
            return ResponseEntity.ok(response);
        } catch (UsernameTakenException e) { // Catch the specific exception
            return ResponseEntity.status(HttpStatus.CONFLICT).body(
                    Map.of("message", "Username already exists") // Changed 'error' to 'message' for consistency with AuthResponse
            );
        } catch (InvalidRequestException e) {
            return ResponseEntity.badRequest().body(
                    Map.of("message", e.getMessage()) // Changed 'error' to 'message'
            );
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody AuthRequest request) {
        try {
            AuthResponse response = authService.authenticate(request);
            System.out.println("Login successful, token: " + response.getToken());
            return ResponseEntity.ok(response);
        } catch (BadCredentialsException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(
                    Map.of("message", "Invalid username or password") // Changed 'error' to 'message'
            );
        }
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validateToken(Authentication authentication) {
        if (authentication != null && authentication.isAuthenticated()) {
            return ResponseEntity.ok(Map.of("message", "Token is valid", "username", authentication.getName()));
        }
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "Invalid or missing token")); // Changed 'error' to 'message'
    }
}