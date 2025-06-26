package com.devops25.gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.BodyInserters;
import reactor.core.publisher.Mono;
import org.springframework.http.server.reactive.ServerHttpRequest;
import reactor.netty.http.client.HttpClient;

import java.net.ConnectException;
import java.time.Duration;
import java.util.concurrent.TimeoutException;

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
       /* this.webClient = webClientBuilder.build(); */
        // Configure HttpClient with timeouts
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofSeconds(15)); // Set a response timeout, e.g., 15 seconds

        this.webClient = webClientBuilder
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }
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
        String fullUrl = userServiceUrl + "/api/auth/register";
        System.out.println("Attempting to register user. Forwarding request to: " + fullUrl); // Log the full URL

        return webClient.post()
                .uri(fullUrl)
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofSeconds(30)) // Increase timeout to 30 seconds
                .map(response -> {
                    System.out.println("Registration success: " + response);
                    return ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(response);
                })
                .onErrorResume(e -> {
                    String errorMessage = "Unknown error";
                    if (e instanceof TimeoutException) {
                        errorMessage = "Request timed out after 30 seconds.";
                    } else if (e instanceof ConnectException) {
                        errorMessage = "Connection refused to the user service.";
                    } else {
                        errorMessage = "An unexpected error occurred: " + e.getMessage();
                    }
                    System.err.println("Registration failed: " + errorMessage);
                    e.printStackTrace(); // Print the full stack trace for more details
                    return Mono.just(ResponseEntity.status(500)
                            .body("{\"error\": \"Registration service unavailable - " + errorMessage + "\"}"));
                });
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