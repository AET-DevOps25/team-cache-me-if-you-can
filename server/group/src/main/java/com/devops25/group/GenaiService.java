package com.devops25.group;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class GenaiService {

    private static final Logger logger = LoggerFactory.getLogger(GenaiService.class);
    private final WebClient webClient;

    public GenaiService(WebClient.Builder webClientBuilder, @Value("${genai.service.url}") String genaiServiceUrl) {
        this.webClient = webClientBuilder.baseUrl(genaiServiceUrl).build();
    }

    public Mono<String> uploadDocument(String groupId, MultipartFile file) throws IOException {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", file.getBytes(), MediaType.APPLICATION_PDF)
                .filename(file.getOriginalFilename());

        logger.info("Forwarding document to genai-service. Group ID: {}, Filename: {}", groupId, file.getOriginalFilename());

        return webClient.post()
                .uri("/documents/upload")
                .header("X-Group-ID", groupId)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(String.class)
                .doOnSuccess(response -> logger.info("Successfully received response from genai-service for group ID: {}", groupId))
                .doOnError(error -> logger.error("Error response from genai-service for group ID: {}", groupId, error));
    }

    public Mono<String> query(String groupId, String question) {
        return webClient.post()
                .uri("/chat/query/sync")
                .header("X-Group-ID", groupId)
                .contentType(MediaType.APPLICATION_JSON)
                .body(BodyInserters.fromValue("{\"question\": \"" + question + "\"}"))
                .retrieve()
                .bodyToMono(String.class);
    }
} 