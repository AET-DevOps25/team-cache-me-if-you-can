package com.devops25.user.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class AuthResponse {
    @JsonProperty("message")
    private String message;
    @JsonProperty("username")
    private String username;
    @JsonProperty("token")
    private String token;
    @JsonProperty("university")
    private String university;


    // MANUALLY ADD GETTERS (TESTING ONLY)
    public String getMessage() { return message; }
    public String getUsername() { return username; }
    public String getToken() { return token; }
    public String getUniversity() { return university; }

}