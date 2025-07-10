    package com.devops25.group;

    import io.jsonwebtoken.Jwts;
    import io.jsonwebtoken.io.Decoders;
    import io.jsonwebtoken.security.Keys;
    import org.springframework.beans.factory.annotation.Value;
    import org.springframework.stereotype.Component;

    @Component
    public class JwtService {
        @Value("${jwt.secret}")
        private String SECRET_KEY;

        public String extractUsername(String token) {
            return Jwts.parserBuilder()
                    .setSigningKey(Keys.hmacShaKeyFor(Decoders.BASE64.decode(SECRET_KEY)))
                    .build()
                    .parseClaimsJws(token)
                    .getBody()
                    .getSubject();
        }
    }