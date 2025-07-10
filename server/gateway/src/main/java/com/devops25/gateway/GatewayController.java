package com.devops25.gateway;

import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.net.ConnectException;
import java.net.URI;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeoutException;

@RestController
@CrossOrigin(origins = {"https://cache-me-if-you-can-genai-client.student.k8s.aet.cit.tum.de",
        "http://localhost",
        "http://localhost:3000",
        "*",},   allowedHeaders = {"*"},
        methods        = {RequestMethod.GET,
                RequestMethod.POST,
                RequestMethod.PUT,
                RequestMethod.DELETE,
                RequestMethod.OPTIONS})

public class GatewayController {

    private final WebClient webClient;

    @Value("${user.service.url}")
    private String userServiceUrl;

    @Value("${files.service.url}")
    private String filesServiceUrl;

    @Value("${genai.service.url}")
    private String genaiServiceUrl;


    private final WebClient.Builder webClientBuilder;
    private final JwtService jwtService;

    public GatewayController(WebClient.Builder webClientBuilder, WebClient.Builder webClientBuilder1, JwtService jwtService) {
        this.webClientBuilder = webClientBuilder1;
        this.jwtService = jwtService;
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
    @GetMapping("/api/auth/validate")
    public Mono<ResponseEntity<String>> validateToken(ServerHttpRequest request) {
        return webClient
                .method(HttpMethod.GET)
                .uri(userServiceUrl + "/api/auth/validate")
                .headers(h -> request.getHeaders().getOrEmpty("Authorization")
                        .forEach(token -> h.set("Authorization", token)))
                .retrieve()
                .toEntity(String.class)
                .onErrorReturn(
                        ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                                .body("{\"message\":\"Auth service unavailable\"}")
                );
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
    @RequestMapping("/api/v1/groups/**")
    public Mono<ResponseEntity<String>> routeToGroupService(
            ServerHttpRequest request,
            @RequestBody(required = false) String body) {

        URI requestUri  = request.getURI();
        String incomingPath     = requestUri.getPath();
        String query    = requestUri.getRawQuery();
        String targetUrl   = "http://group:8083" + incomingPath + (query != null ? "?" + query : "");
        String incomingMethod = request.getMethod().name();

        /*
        String incomingPath   = request.getURI().getPath();
        String incomingMethod = request.getMethod().name();
        String targetUrl      = "http://group:8083" + incomingPath;*/

        System.out.println("--- Gateway Routing to Group Service ---");
        System.out.println("Incoming Path: "       + incomingPath);
        System.out.println("Incoming Method: "     + incomingMethod);
        System.out.println("Target URL: "          + targetUrl);
        System.out.println("Content-Type: "        + request.getHeaders().getFirst("Content-Type"));
        System.out.println("Authorization: "       + request.getHeaders().getFirst("Authorization"));
        System.out.println("Request Body: "        + (body != null ? body : "No body"));

        System.out.println("Incoming Auth header: "
                + request.getHeaders().getFirst("Authorization"));


        // If it's a POST, JWT exists, and we have a body -> inject ownerUsername
        if ("POST".equalsIgnoreCase(incomingMethod)
                && body != null
                && request.getHeaders().getFirst("Authorization") != null
                && request.getHeaders().getFirst("Authorization").startsWith("Bearer ")) {

            String jwt      = request.getHeaders().getFirst("Authorization").substring(7);
            String username = jwtService.extractUsername(jwt);
            System.out.println("Extracted username from JWT: " + username);

            if (username != null) {
                try {
                    // ▶▶ PRODUCTION-READY JSON MODIFICATION
                    ObjectMapper mapper = new ObjectMapper();
                    JsonNode root = mapper.readTree(body);

                    // Ensure it's an object so we can add a field
                    if (root.isObject()) {
                        ((ObjectNode) root).put("ownerUsername", username);
                        body = mapper.writeValueAsString(root);
                        System.out.println("Modified Request Body for Group Service: " + body);
                    } else {
                        System.err.println("Expected JSON object but got: " + root.getNodeType());
                    }
                } catch (Exception e) {
                    System.err.println("Error parsing/modifying JSON body: " + e.getMessage());
                    e.printStackTrace();
                }
            } else {
                System.err.println("Username could not be extracted from JWT.");
            }
        }

        // Forward the (possibly modified) request on to the group service
        return webClientBuilder.build()
                .method(request.getMethod())
                .uri(targetUrl)
                .headers(headers -> request.getHeaders().forEach(headers::addAll))
                .body(Optional.ofNullable(body)
                        .map(BodyInserters::fromValue)
                        .orElse(BodyInserters.empty()))
                .retrieve()
                .toEntity(String.class)
                .doOnSuccess(resp ->
                        System.out.println("Group Service response OK for [" + incomingPath + "]: " + resp.getBody()))
                .doOnError(e -> {
                    String status = (e instanceof WebClientResponseException)
                            ? String.valueOf(((WebClientResponseException)e).getStatusCode())
                            : "UNKNOWN";
                    System.err.println("Group Service error: HTTP " + status + " - " + e.getMessage());
                    e.printStackTrace();
                })
                .onErrorResume(e ->
                        Mono.just(ResponseEntity
                                .status(HttpStatus.BAD_GATEWAY)
                                .body("{\"error\":\"Group service unavailable\"}")));
    }

}