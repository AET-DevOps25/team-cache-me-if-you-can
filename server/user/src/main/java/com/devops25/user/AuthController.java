package com.devops25.user;

import com.devops25.user.dto.AuthRequest;
import com.devops25.user.dto.AuthResponse;
import com.devops25.user.exceptions.InvalidRequestException;
import com.devops25.user.exceptions.UsernameTakenException;
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
        } catch (UsernameTakenException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(
                    Map.of("error", "Username already taken")
            );
        } catch (InvalidRequestException e) {
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
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
                    Map.of("error", "Invalid username or password")
            );
        }
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validateToken(Authentication authentication) {
        // If the request reaches this point, it means the JWT filter has
        // successfully authenticated the user and set the Authentication object.
        if (authentication != null && authentication.isAuthenticated()) {
            return ResponseEntity.ok(Map.of("message", "Token is valid", "username", authentication.getName()));
        }
        // This part should ideally not be reached if security is configured correctly,
        // as invalid tokens would be rejected by the filter before reaching the controller.
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid or missing token"));
    }
}
