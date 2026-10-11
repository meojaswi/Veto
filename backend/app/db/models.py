
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    website_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )


class OrderContext(Base):
    __tablename__ = "order_contexts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # External order identifier from the source platform.
    order_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    platform_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platforms.id"),
        nullable=False,
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brands.id"),
        nullable=False,
    )

    product_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Records when this order context was imported into Veto.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Return(Base):
    __tablename__ = "returns"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    # Multiple return requests can reference the same order context.
    order_context_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("order_contexts.id"),
        nullable=False,
        index=True,
    )

    reason: Mapped[str] = mapped_column(Text)
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ReturnDecision(Base):
    __tablename__ = "return_decisions"

    return_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("returns.id"),
        primary_key=True,
    )
    decision: Mapped[str] = mapped_column(String(32))
    rationale: Mapped[str] = mapped_column(Text)
    governance_action: Mapped[str] = mapped_column(String(32))
    intake_errors: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )


class ReturnPolicy(Base):
    __tablename__ = "return_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    platform_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("platforms.id"),
        nullable=True,
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("brands.id"),
        nullable=True,
    )

    product_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    __table_args__ = (
        UniqueConstraint(
            "policy_id",
            "version_number",
            name="uq_policy_version_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("return_policies.id"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    source_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("policy_versions.id"),
        nullable=False,
    )
    rule_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    operator: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    value: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class PolicyEvaluation(Base):
    __tablename__ = "policy_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    return_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("returns.id"),
        nullable=False,
    )
    policy_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("policy_versions.id"),
        nullable=True,
    )
    outcome: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    matched_rules: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evidence: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
