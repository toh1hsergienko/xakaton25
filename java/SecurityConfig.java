package com.example.laba4.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/products/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(login -> login
                .loginPage("/products/login")
                .defaultSuccessUrl("/products")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/products/logout")
                .logoutSuccessUrl("/products/login")
                .permitAll()
            );
        return http.build();
    }
}