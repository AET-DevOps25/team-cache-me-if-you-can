package com.devops25.gateway;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureAlgorithm; // Still needed for Key setup, but not for generation
import io.jsonwebtoken.SignatureException; // For catching invalid signatures
import io.jsonwebtoken.UnsupportedJwtException; // For catching unsupported JWTs
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;
import java.util.function.Function;

@Component
public class JwtService {

    // Load SECRET_KEY from application.properties or environment variables
    @Value("${jwt.secret}")
    private String SECRET_KEY;

    // Only methods strictly needed by the Gateway are kept

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    /**
     * Validates a JWT token's signature and expiration.
     * The Gateway only needs to trust the token was issued correctly and is not expired.
     * Blacklist checks are handled by the User Service itself.
     *
     * @param token The JWT string.
     * @return true if the token is valid (signature OK, not expired), false otherwise.
     */
    public boolean isTokenValid(String token) {
        try {
            // Attempt to parse claims. If successful, signature is good.
            extractAllClaims(token);
            // Then check expiration.
            return !isTokenExpired(token);
        } catch (SignatureException e) {
            System.err.println("Invalid JWT signature: " + e.getMessage());
        } catch (MalformedJwtException e) {
            System.err.println("Invalid JWT token: " + e.getMessage());
        } catch (ExpiredJwtException e) {
            System.err.println("JWT token is expired: " + e.getMessage());
        } catch (UnsupportedJwtException e) {
            System.err.println("JWT token is unsupported: " + e.getMessage());
        } catch (IllegalArgumentException e) {
            System.err.println("JWT claims string is empty: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("An unexpected error occurred during JWT validation: " + e.getMessage());
        }
        return false;
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private Claims extractAllClaims(String token) {
        // Ensure SECRET_KEY is not null or empty before decoding
        if (SECRET_KEY == null || SECRET_KEY.isEmpty()) {
            throw new IllegalStateException("JWT Secret Key is not configured.");
        }
        return Jwts
                .parserBuilder()
                .setSigningKey(getSignInKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    private Key getSignInKey() {
        byte[] keyBytes = Decoders.BASE64.decode(SECRET_KEY);
        return Keys.hmacShaKeyFor(keyBytes);
    }
}