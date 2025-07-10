package com.devops25.user;

import com.devops25.user.config.JwtService;
import com.devops25.user.dto.AuthRequest;
import com.devops25.user.dto.AuthResponse;
import com.devops25.user.exceptions.InvalidRequestException;
import com.devops25.user.exceptions.UsernameTakenException; // NEW Import
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository repository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;
    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    // Modified register method
    public AuthResponse register(AuthRequest request) {
        if (request.getUsername() == null || request.getPassword() == null) {
            throw new InvalidRequestException("Username and password are required");
        }

        if (repository.findByUsername(request.getUsername()).isPresent()) {
            throw new UsernameTakenException("Username already exists"); // NEW: Throw exception
        }

        var user = User.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .university(request.getUniversity())
                .build();
        repository.save(user);

        return AuthResponse.builder()
                .message("Registration successful")
                .username(user.getUsername())
                .build();
    }

    public AuthResponse authenticate(AuthRequest request) {
        if (request.getUsername() == null || request.getPassword() == null) {
            throw new InvalidRequestException("Username and password are required");
        }

        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getUsername(),
                        request.getPassword()
                )
        );

        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        String token = jwtService.generateToken(userDetails);

        User user = repository.findByUsername(userDetails.getUsername())
                .orElseThrow(() -> new InvalidRequestException("User not found after authentication"));

        return AuthResponse.builder()
                .message("Login successful")
                .username(userDetails.getUsername())
                .token(token)
                .university(user.getUniversity()) // Include university in response
                .build();
    }
}