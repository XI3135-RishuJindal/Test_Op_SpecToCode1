package com.example.userrolemanagement.domain.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Core domain entity representing a UserRole assignment.
 * Tracks which roles have been assigned to a given user (identified by external userId).
 */
@Entity
@Table(name = "user_roles",
        uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "role_id"}))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserRole {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    /** External user identifier supplied by the authentication service. */
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "role_id", nullable = false)
    private Role role;

    @Column(name = "assigned_at", nullable = false, updatable = false)
    private Instant assignedAt;

    @PrePersist
    protected void onCreate() {
        this.assignedAt = Instant.now();
    }
}
