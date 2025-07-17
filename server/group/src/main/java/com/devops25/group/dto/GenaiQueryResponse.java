package com.devops25.group.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GenaiQueryResponse {
    private String answer;
    private List<SourceDocument> sourceDocuments;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SourceDocument {
        private String pageContent;
        private Metadata metadata;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Metadata {
        private String source;
        private Integer pageNumber;
    }
} 