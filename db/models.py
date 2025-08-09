from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .session import Base


class Referral(Base):
    __tablename__ = "giveaway_referrals"

    giveaway_id: Mapped[int] = mapped_column(
        ForeignKey("giveaways.id"), primary_key=True
    )
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    giveaway: Mapped["Giveaway"] = relationship(
        "Giveaway", back_populates="referrals", lazy="selectin"
    )
    referrer: Mapped["User"] = relationship(
        "User",
        back_populates="referrals_sent",
        foreign_keys=[referrer_id],
        lazy="selectin",
    )
    referred: Mapped["User"] = relationship(
        "User",
        back_populates="referrals_received",
        foreign_keys=[referred_id],
        lazy="selectin",
    )


class GiveawayUser(Base):
    __tablename__ = "giveaway_users"

    giveaway_id: Mapped[int] = mapped_column(
        ForeignKey("giveaways.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    giveaway: Mapped["Giveaway"] = relationship(
        "Giveaway", back_populates="giveaway_users"
    )
    user: Mapped["User"] = relationship("User", back_populates="giveaway_users")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    created_giveaways: Mapped[list["Giveaway"]] = relationship(
        "Giveaway",
        back_populates="creator",
        lazy="selectin",
    )

    giveaway_users: Mapped[list["GiveawayUser"]] = relationship(
        "GiveawayUser",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    giveaways: Mapped[list["Giveaway"]] = relationship(
        "Giveaway",
        secondary="giveaway_users",
        back_populates="users",
        lazy="selectin",
        viewonly=True,
    )

    referrals_sent: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="referrer",
        foreign_keys="[Referral.referrer_id]",
        lazy="selectin",
    )

    referrals_received: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="referred",
        foreign_keys="[Referral.referred_id]",
        lazy="selectin",
    )

    channels: Mapped[list["Channel"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Giveaway(Base):
    __tablename__ = "giveaways"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
    sharing: Mapped[bool] = mapped_column(default=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_giveaways",
        lazy="selectin",
    )

    giveaway_users: Mapped[list["GiveawayUser"]] = relationship(
        "GiveawayUser",
        back_populates="giveaway",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="giveaway_users",
        back_populates="giveaways",
        lazy="selectin",
        viewonly=True,
    )

    referrals: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="giveaway",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="channels", lazy="selectin")
