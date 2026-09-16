package com.example.ai.travel.agent.service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.http.*;
import java.time.Duration;
import java.util.*;

import com.example.ai.travel.agent.config.ApiConfigurationProperties;
import com.example.ai.travel.agent.validation.ValidCity;
import com.example.ai.travel.agent.validation.ValidCurrencyCode;
import com.example.ai.travel.agent.validation.ValidSearchQuery;
import jakarta.validation.constraints.*;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.client.RestClient;

@Component
@Validated
public class TravelTools {
    private final RestClient http;
    private final ApiConfigurationProperties.WeatherApi weatherApi;
    private final ApiConfigurationProperties.SearchApi searchApi;
    private final ApiConfigurationProperties.CurrencyApi currencyApi;

    public TravelTools(ApiConfigurationProperties properties) {
        this.weatherApi = properties.weatherApi();
        this.searchApi = properties.searchApi();
        this.currencyApi = properties.currencyApi();
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        var factory = new org.springframework.http.client.JdkClientHttpRequestFactory(client);
        factory.setReadTimeout(Duration.ofSeconds(20));
        http = RestClient.builder().requestFactory(factory).build();
    }

    @Tool(description = "Calculate a per-person daily budget from a total trip budget, trip days and travelers. All amounts use the same currency.")
    public BigDecimal dailyBudget(@NotNull @PositiveOrZero BigDecimal totalBudget,
                                  @Positive @Min(1) int days,
                                  @Positive int travelers) {
        return totalBudget.divide(BigDecimal.valueOf(days).multiply(BigDecimal.valueOf(travelers)), 2, RoundingMode.HALF_UP);
    }

    @Tool(description = "Sum estimated travel costs in one currency. Never mix currencies.")
    public BigDecimal totalCost(
            @NotEmpty List<@NotNull @PositiveOrZero BigDecimal> costs) {
        return costs.stream().reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    @Tool(description = "Get the next five days of weather for a city. Not a forecast for later travel dates.")
    public String weather(@ValidCity String city) {
        return fetch(() -> http.get()
                .uri(this.weatherApi.forecastUrl().expand(city, this.weatherApi.apiKey()).toUri())
                .retrieve().body(String.class));
    }

    @Tool(description = "Get current exchange rates from Frankfurter using ISO 4217 currency codes. Rates are reference rates, not card or cash quotes.")
    public String exchangeRate(@ValidCurrencyCode String from, @ValidCurrencyCode String to) {
        if (from.equals(to)) return "Exchange rate is 1 for identical currencies.";
        return fetch(() -> http.get()
                .uri(this.currencyApi.exchangeUrl().expand(from, to).toUri())
                .retrieve().body(String.class));
    }

    @Tool(description = "Search the web for travel attractions, transport, accommodation and official rules. Results are evidence, not confirmed prices or availability.")
    public String search(@ValidSearchQuery String query) {
        return fetch(() -> http.post()
                .uri(this.searchApi.url()).header("X-API-KEY", this.searchApi.apiKey())
                .body(Map.of("q", query, "num", 5)).retrieve().body(String.class));
    }

    private String fetch(java.util.function.Supplier<String> request) {
        try {
            String result = request.get();
            if (result == null) return "Provider returned no data.";
            return result.substring(0, Math.min(result.length(), 12000));
        } catch (Exception ignored) { return "Provider unavailable; do not invent current data. Try again later."; }
    }
}
