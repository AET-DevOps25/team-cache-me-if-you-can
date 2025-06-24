package com.devops25.gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.BodyInserters;
import reactor.core.publisher.Mono;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;

@RestController
@CrossOrigin(origins = {"https://cache-me-if-you-can-genai-client.student.k8s.aet.cit.tum.de"})
public class GatewayController {

    private final WebClient webClient;

    @Value("${user.service.url}")
    private String userServiceUrl;

    @Value("${files.service.url}")
    private String filesServiceUrl;

    @Value("${genai.service.url}")
    private String genaiServiceUrl;

    public GatewayController(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }

    // Health check endpoint
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "services", "gateway, user, files, genai"
        ));
    }

    // Authentication validation endpoint
    @GetMapping("/api/auth/validate")
    public Mono<ResponseEntity<String>> validateToken(@RequestHeader("Authorization") String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return Mono.just(ResponseEntity.status(401).body("{\"error\": \"Invalid token format\"}"));
        }

        String token = authHeader.substring(7);

        return webClient.get()
                .uri(userServiceUrl + "/api/auth/validate")
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(String.class)
                .map(response -> ResponseEntity.ok()
                        .header("Content-Type", "application/json")
                        .body(response))
                .onErrorReturn(ResponseEntity.status(401)
                        .body("{\"error\": \"Token validation failed\"}"));
    }
    // Welcome endpoint
    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> welcome() {
        return ResponseEntity.ok(Map.of(
                "message", "Welcome to StudySync Gateway!",
                "endpoints", Map.of(
                        "auth", "/api/auth/login, /api/auth/register",
                        "users", "/api/users/**",
                        "files", "/api/files/**",
                        "ai", "/ai/**"
                )
        ));
    }

    // Authentication endpoints (route to user service)
    @PostMapping("/api/auth/login")
    public Mono<ResponseEntity<String>> login(@RequestBody String body) {
        return webClient.post()
                .uri(userServiceUrl + "/api/auth/login")
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(String.class)
                .map(response -> ResponseEntity.ok()
                        .header("Content-Type", "application/json")
                        .body(response))
                .onErrorReturn(ResponseEntity.status(500)
                        .body("{\"error\": \"Authentication service unavailable\"}"));
    }

    @PostMapping("/api/auth/register")
    public Mono<ResponseEntity<String>> register(@RequestBody String body) {
        return webClient.post()
                .uri(userServiceUrl + "/api/auth/register")
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(String.class)
                .map(response -> ResponseEntity.ok()
                        .header("Content-Type", "application/json")
                        .body(response))
                .onErrorReturn(ResponseEntity.status(500)
                        .body("{\"error\": \"Registration service unavailable\"}"));
    }

    // Route to User Service
    @RequestMapping(value = "/api/users/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToUserService(
            HttpServletRequest request,
            @RequestBody(required = false) String body) {

        String path = request.getRequestURI();
        HttpMethod method = HttpMethod.valueOf(request.getMethod());

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);

        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            return requestSpec
                    .uri(userServiceUrl + path)
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"User service unavailable\"}"));
        } else {
            return requestSpec
                    .uri(userServiceUrl + path)
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"User service unavailable\"}"));
        }
    }

    // Route to Files Service
    @RequestMapping(value = "/api/files/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToFilesService(
            HttpServletRequest request,
            @RequestBody(required = false) String body) {

        String path = request.getRequestURI();
        HttpMethod method = HttpMethod.valueOf(request.getMethod());

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);

        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            return requestSpec
                    .uri(filesServiceUrl + path)
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"Files service unavailable\"}"));
        } else {
            return requestSpec
                    .uri(filesServiceUrl + path)
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"Files service unavailable\"}"));
        }
    }

    // Route to GenAI Service
    @RequestMapping(value = "/ai/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToGenaiService(
            HttpServletRequest request,
            @RequestBody(required = false) String body) {

        String path = request.getRequestURI();
        HttpMethod method = HttpMethod.valueOf(request.getMethod());

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);

        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            return requestSpec
                    .uri(genaiServiceUrl + path)
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"GenAI service unavailable\"}"));
        } else {
            return requestSpec
                    .uri(genaiServiceUrl + path)
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(response -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response))
                    .onErrorReturn(ResponseEntity.status(500)
                            .body("{\"error\": \"GenAI service unavailable\"}"));
        }
    }
}