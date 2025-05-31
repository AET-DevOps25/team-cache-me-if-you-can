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
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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

    /*
    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            // Optionally add token to a blacklist here, e.g.:
            // tokenBlacklistService.blacklistToken(token);
            return ResponseEntity.ok(Map.of("message", "Logout successful"));
        }
        return ResponseEntity.badRequest().body(Map.of("error", "Invalid token"));
    }*/

}
