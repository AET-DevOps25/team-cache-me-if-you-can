package com.devops25.gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.BodyInserters;
import reactor.core.publisher.Mono;
import org.springframework.http.server.reactive.ServerHttpRequest;
import reactor.netty.http.client.HttpClient;
import java.net.ConnectException; // Import these
import java.util.concurrent.TimeoutException; // Import these

import java.net.ConnectException;
import java.time.Duration;
import java.util.concurrent.TimeoutException;

@RestController
@CrossOrigin(origins = {"https://cache-me-if-you-can-genai-client.student.k8s.aet.cit.tum.de",
        "http://localhost",
        "http://localhost:3000",})
public class GatewayController {

    private final WebClient webClient;

    @Value("${user.service.url}")
    private String userServiceUrl;

    @Value("${files.service.url}")
    private String filesServiceUrl;

    @Value("${genai.service.url}")
    private String genaiServiceUrl;

    @Value("${group.service.url}") // <-- NEW: Group Service URL
    private String groupServiceUrl;

    public GatewayController(WebClient.Builder webClientBuilder) {
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofSeconds(15));

        this.webClient = webClientBuilder
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }

    @PostMapping("/api/auth/login")
    public Mono<ResponseEntity<String>> login(@RequestBody String body) {
        return webClient.post()
                .uri(userServiceUrl + "/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
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
        System.out.println("Attempting to register user. Forwarding request to: " + fullUrl);

        return webClient.post()
                .uri(fullUrl)
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofSeconds(30))
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
                    e.printStackTrace();
                    return Mono.just(ResponseEntity.status(500)
                            .body("{\"error\": \"Registration service unavailable - " + errorMessage + "\"}"));
                });
    }

    // Route to User Service
    @RequestMapping(value = "/api/users/**", method = {
            RequestMethod.GET, RequestMethod.POST,
            RequestMethod.PUT, RequestMethod.DELETE
    })
    public Mono<ResponseEntity<String>> routeToUserService(
            ServerHttpRequest request,
            @RequestBody(required = false) String body
    ) {
        String path = request.getPath().pathWithinApplication().value();
        HttpMethod method = request.getMethod();

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);
        requestSpec.headers(h -> {
            var incoming = request.getHeaders();
            if (incoming.getContentType() != null) {
                h.setContentType(incoming.getContentType());
            }
            incoming.getOrEmpty("Authorization")
                    .stream().findFirst()
                    .ifPresent(token -> h.set("Authorization", token));
        });

        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            return requestSpec
                    .uri(userServiceUrl + path)
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(resp -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(resp))
                    .onErrorReturn(ResponseEntity.status(502)
                            .body("{\"error\": \"User service unavailable\"}"));
        } else {
            return requestSpec
                    .uri(userServiceUrl + path)
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(resp -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(resp))
                    .onErrorReturn(ResponseEntity.status(502)
                            .body("{\"error\": \"User service unavailable\"}"));
        }
    }

    // Route to Files Service
    @RequestMapping(value = "/api/files/**", method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE})
    public Mono<ResponseEntity<String>> routeToFilesService(
            ServerHttpRequest request,
            @RequestBody(required = false) String body) {

        String path = request.getPath().pathWithinApplication().value();
        HttpMethod method = request.getMethod();

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);
        requestSpec.headers(h -> {
            var incoming = request.getHeaders();
            if (incoming.getContentType() != null) {
                h.setContentType(incoming.getContentType());
            }
            incoming.getOrEmpty("Authorization")
                    .stream().findFirst()
                    .ifPresent(token -> h.set("Authorization", token));
        });

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
            ServerHttpRequest request,
            @RequestBody(required = false) String body) {

        String path = request.getPath().pathWithinApplication().value();
        HttpMethod method = request.getMethod();

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);
        requestSpec.headers(h -> {
            var incoming = request.getHeaders();
            if (incoming.getContentType() != null) {
                h.setContentType(incoming.getContentType());
            }
            incoming.getOrEmpty("Authorization")
                    .stream().findFirst()
                    .ifPresent(token -> h.set("Authorization", token));
        });

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

    /*
    // NEW: Route to Group Service
    @RequestMapping(value = "/api/v1/groups/**", method = {
            RequestMethod.GET, RequestMethod.POST,
            RequestMethod.PUT, RequestMethod.DELETE
    })
    public Mono<ResponseEntity<String>> routeToGroupService(
            ServerHttpRequest request,
            @RequestBody(required = false) String body
    ) {
        String path = request.getPath().pathWithinApplication().value();
        HttpMethod method = request.getMethod();

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);
        requestSpec.headers(h -> {
            var incoming = request.getHeaders();
            if (incoming.getContentType() != null) {
                h.setContentType(incoming.getContentType());
            }
            incoming.getOrEmpty("Authorization")
                    .stream().findFirst()
                    .ifPresent(token -> h.set("Authorization", token));
        });

        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            return requestSpec
                    .uri(groupServiceUrl + path) // <-- Use groupServiceUrl
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(resp -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(resp))
                    .onErrorReturn(ResponseEntity.status(502)
                            .body("{\"error\": \"Group service unavailable\"}"));
        } else {
            return requestSpec
                    .uri(groupServiceUrl + path) // <-- Use groupServiceUrl
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(resp -> ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(resp))
                    .onErrorReturn(ResponseEntity.status(502)
                            .body("{\"error\": \"Group service unavailable\"}"));
        }
    }*/

    // NEW: Route to Group Service
    @RequestMapping(value = "/api/v1/groups/**", method = {
            RequestMethod.GET, RequestMethod.POST,
            RequestMethod.PUT, RequestMethod.DELETE
    })
    public Mono<ResponseEntity<String>> routeToGroupService(
            ServerHttpRequest request,
            @RequestBody(required = false) String body
    ) {
        String path = request.getPath().pathWithinApplication().value();
        HttpMethod method = request.getMethod();
        String targetUrl = groupServiceUrl + path; // Pre-calculate for logging

        System.out.println("--- Gateway Routing to Group Service ---");
        System.out.println("Incoming Path: " + path);
        System.out.println("Incoming Method: " + method);
        System.out.println("Target URL: " + targetUrl);
        System.out.println("Incoming Content-Type: " + request.getHeaders().getContentType());
        System.out.println("Incoming Authorization: " + request.getHeaders().getFirst("Authorization"));
        System.out.println("Request Body received by Gateway: " + (body != null ? body.substring(0, Math.min(body.length(), 500)) : "[No body or null]")); // Print first 500 chars

        WebClient.RequestBodyUriSpec requestSpec = webClient.method(method);
        requestSpec.headers(h -> {
            var incoming = request.getHeaders();
            if (incoming.getContentType() != null) {
                h.setContentType(incoming.getContentType());
            }
            // Forward all incoming headers except host (handled by changeOrigin)
            incoming.forEach((name, values) -> {
                if (!name.equalsIgnoreCase("Host") && !name.equalsIgnoreCase("Content-Length")) { // Content-Length will be re-calculated by WebClient
                    h.addAll(name, values);
                }
            });
        });

        Mono<String> responseMono;
        if (body != null && (method == HttpMethod.POST || method == HttpMethod.PUT)) {
            responseMono = requestSpec
                    .uri(targetUrl)
                    .body(BodyInserters.fromValue(body))
                    .retrieve()
                    .bodyToMono(String.class);
        } else {
            responseMono = requestSpec
                    .uri(targetUrl)
                    .retrieve()
                    .bodyToMono(String.class);
        }

        return responseMono
                .map(resp -> {
                    System.out.println("Group Service response successful for [" + path + "]: " + resp.substring(0, Math.min(resp.length(), 500))); // Log success
                    return ResponseEntity.ok()
                            .header("Content-Type", "application/json")
                            .body(resp);
                })
                .doOnError(e -> { // Capture the actual error
                    String errorMessage = "Unknown error from Group Service:";
                    if (e instanceof ConnectException) {
                        errorMessage = "Connection refused to Group Service at " + targetUrl;
                    } else if (e instanceof TimeoutException) {
                        errorMessage = "Timeout connecting to Group Service at " + targetUrl;
                    } else if (e instanceof org.springframework.web.reactive.function.client.WebClientResponseException) {
                        org.springframework.web.reactive.function.client.WebClientResponseException wcException = (org.springframework.web.reactive.function.client.WebClientResponseException) e;
                        errorMessage = "Group Service returned HTTP " + wcException.getStatusCode() + " - " + wcException.getResponseBodyAsString();
                    } else {
                        errorMessage = "An unexpected error occurred while calling Group Service at " + targetUrl + ":";
                    }
                    System.err.println(errorMessage);
                    e.printStackTrace(); // Print stack trace for full details
                })
                .onErrorReturn(ResponseEntity.status(502)
                        .body("{\"error\": \"Group service unavailable\"}"));
    }
}