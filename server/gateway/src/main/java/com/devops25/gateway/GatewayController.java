package com.devops25.gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@RestController
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

    // Health check endpoint (simple implementation)
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Gateway is healthy");
    }

    // Welcome/info endpoint
    @GetMapping("/")
    public ResponseEntity<String> welcome() {
        return ResponseEntity.ok("Welcome to StudySync Gateway! Available endpoints: /api/users, /api/files, /ai");
    }

    // Route to User Service
    @RequestMapping(value = "/api/users/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToUserService(
            @RequestBody(required = false) String body,
            @RequestParam(required = false) String params,
            @RequestHeader(required = false) String headers) {

        String path = "/api/users" + getPathAfter("/api/users");

        return webClient.get()
                .uri(userServiceUrl + path)
                .retrieve()
                .bodyToMono(String.class)
                .map(ResponseEntity::ok)
                .onErrorReturn(ResponseEntity.status(500).body("User service unavailable"));
    }

    // Route to Files Service
    @RequestMapping(value = "/api/files/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToFilesService(
            @RequestBody(required = false) String body) {

        String path = "/api/files" + getPathAfter("/api/files");

        return webClient.get()
                .uri(filesServiceUrl + path)
                .retrieve()
                .bodyToMono(String.class)
                .map(ResponseEntity::ok)
                .onErrorReturn(ResponseEntity.status(500).body("Files service unavailable"));
    }

    // Route to GenAI Service
    @RequestMapping(value = "/ai/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToGenaiService(
            @RequestBody(required = false) String body) {

        String path = "/ai" + getPathAfter("/ai");

        return webClient.get()
                .uri(genaiServiceUrl + path)
                .retrieve()
                .bodyToMono(String.class)
                .map(ResponseEntity::ok)
                .onErrorReturn(ResponseEntity.status(500).body("GenAI service unavailable"));
    }

    private String getPathAfter(String prefix) {
        // This is a simplified implementation - you'd want to use proper request path extraction
        return ""; // For now, just route to root of each service
    }
}