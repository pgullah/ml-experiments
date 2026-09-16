package com.example.ai.travel.agent.config;

import jakarta.validation.constraints.NotNull;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.util.UriComponents;

@ConfigurationProperties("api-config")
@Validated
public record ApiConfigurationProperties(@NotNull WeatherApi weatherApi,
                                         @NotNull SearchApi searchApi,
                                         @NotNull CurrencyApi currencyApi,
                                         @NotNull TravelApi travelApi) {

    public record WeatherApi(@NotNull String apiKey, @NotNull UriComponents forecastUrl){}

    public record SearchApi(@NotNull String apiKey, @NotNull String url){}

    public record CurrencyApi(@NotNull UriComponents exchangeUrl) {}

    public record TravelApi(@NotNull String apiKey) {}

}