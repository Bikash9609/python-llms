from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
    Float,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from faker import Faker
import random
from datetime import datetime
from config import config


Base = declarative_base()
fake = Faker()

# Association Table (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    employees = relationship("User", back_populates="department")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")
    roles = relationship("Role", secondary=user_roles, backref="users")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    inventory = Column(Integer)
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    action = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


# Connect to Postgres
engine = create_engine(
    f"postgresql://postgres:postgres@localhost/{config.get('database_name')}"
)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Seeding Logic
def seed_data():
    roles = [Role(name=r) for r in ["Admin", "Editor", "Viewer"]]
    session.add_all(roles)

    departments = [Department(name=fake.company()) for _ in range(10)]
    session.add_all(departments)

    users = []
    for _ in range(200):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            department=random.choice(departments),
            roles=random.sample(roles, k=random.randint(1, 2)),
        )
        users.append(user)
    session.add_all(users)

    products = [
        Product(
            name=fake.word(),
            price=random.uniform(10, 500),
            inventory=random.randint(1, 100),
        )
        for _ in range(100)
    ]
    session.add_all(products)

    orders = []
    for _ in range(300):
        user = random.choice(users)
        order = Order(user=user)
        session.add(order)
        for _ in range(random.randint(1, 5)):
            item = OrderItem(
                order=order,
                product=random.choice(products),
                quantity=random.randint(1, 3),
            )
            session.add(item)

    posts = []
    for _ in range(200):
        post = Post(
            title=fake.sentence(), content=fake.text(), author=random.choice(users)
        )
        posts.append(post)
    session.add_all(posts)

    for _ in range(500):
        comment = Comment(
            content=fake.text(), post=random.choice(posts), user=random.choice(users)
        )
        session.add(comment)

    for _ in range(300):
        log = AuditLog(
            action=random.choice(["CREATE", "UPDATE", "DELETE"]),
            user_id=random.choice(users).id,
        )
        session.add(log)

    session.commit()


seed_data()
print("Database seeded successfully.")
