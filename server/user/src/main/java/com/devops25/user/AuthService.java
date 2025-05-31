package com.devops25.user;

import com.devops25.user.config.JwtService;
import com.devops25.user.dto.AuthRequest;
import com.devops25.user.dto.AuthResponse;
import com.devops25.user.exceptions.InvalidRequestException;
import com.devops25.user.exceptions.UsernameTakenException;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Lazy;
import org.springframework.context.annotation.Primary;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
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



    public AuthResponse register(AuthRequest request) {
        if (request.getUsername() == null || request.getPassword() == null) {
            throw new InvalidRequestException("Username and password are required");
        }

        if (repository.findByUsername(request.getUsername()).isPresent()) {
            return AuthResponse.builder()
                    .message("Username already exists")
                    .build();
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

    // AuthService.java
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

        // Get UserDetails instead of domain User
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        String token = jwtService.generateToken(userDetails);

        return AuthResponse.builder()
                .message("Login successful")
                .username(userDetails.getUsername())
                .token(token)
                .build();
    }
}
