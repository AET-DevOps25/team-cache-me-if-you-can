package com.devops25.gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.BodyInserters;
import reactor.core.publisher.Mono;
import org.springframework.http.server.reactive.ServerHttpRequest;

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

    // ... (existing health, validate, welcome endpoints - no changes needed there)

    // Authentication endpoints (route to user service) - NO CHANGE NEEDED HERE
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
            ServerHttpRequest request, // <-- Changed from HttpServletRequest
            @RequestBody(required = false) String body) {

        String path = request.getPath().pathWithinApplication().value(); // <-- Get path reactively
        HttpMethod method = request.getMethod(); // <-- Get method reactively

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
            ServerHttpRequest request, // <-- Changed from HttpServletRequest
            @RequestBody(required = false) String body) {

        String path = request.getPath().pathWithinApplication().value(); // <-- Get path reactively
        HttpMethod method = request.getMethod(); // <-- Get method reactively

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
            ServerHttpRequest request, // <-- Changed from HttpServletRequest
            @RequestBody(required = false) String body) {

        String path = request.getPath().pathWithinApplication().value(); // <-- Get path reactively
        HttpMethod method = request.getMethod(); // <-- Get method reactively

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