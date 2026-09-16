package com.example.ai.travel.agent.controller;

import com.example.ai.travel.agent.service.ChatService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class MyController {
    private final ChatService service;
    private final byte[] token;
    public MyController(ChatService service, @Value("${travel.api-key}") String token) {
        if (token.isBlank()) throw new IllegalArgumentException("TRAVEL_AGENT_API_KEY must not be blank");
        this.service = service;
        this.token = ("Bearer " + token).getBytes(StandardCharsets.UTF_8);
    }
    public record ChatRequest(@NotBlank @Size(max=8000) String message,
                              @NotBlank @Size(max=256) String thread_id) {}
    public record ChatResponse(String content, String thread_id) {}

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "ok"); }

    @PostMapping("/chat")
    public ChatResponse chat(@RequestHeader(value="Authorization", defaultValue="") String authorization,
                             @Valid @RequestBody ChatRequest request) {
        if (!MessageDigest.isEqual(token, authorization.getBytes(StandardCharsets.UTF_8)))
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or missing API token");
        return new ChatResponse(service.chat(request.message().trim(), request.thread_id().trim()), request.thread_id().trim());
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<Map<String,String>> status(ResponseStatusException error) {
        var builder = ResponseEntity.status(error.getStatusCode());
        if (error.getStatusCode().value() == 401) builder.header("WWW-Authenticate", "Bearer");
        if (error.getStatusCode().value() == 503) builder.header("Retry-After", "1");
        return builder.body(Map.of("error", error.getReason() == null ? "Request failed" : error.getReason()));
    }
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String,String>> failure(Exception error) {
        if (error instanceof org.springframework.web.bind.MethodArgumentNotValidException
                || error instanceof org.springframework.http.converter.HttpMessageNotReadableException)
            return ResponseEntity.badRequest().body(Map.of("error", "Provide a nonblank message (max 8000) and thread_id (max 256)"));
        return ResponseEntity.status(502).body(Map.of("error", "Travel agent request failed; try again later"));
    }
}
