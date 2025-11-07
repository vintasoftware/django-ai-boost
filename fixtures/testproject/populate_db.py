#!/usr/bin/env python
"""
Script to populate the test database with sample data.
Run from project root: uv run python fixtures/testproject/populate_db.py
"""

import os
import sys
from pathlib import Path

# Add testproject to path
testproject_path = Path(__file__).parent
sys.path.insert(0, str(testproject_path))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

import django

django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

from blog.models import Category, Comment, Post, Tag


def populate():
    """Populate the database with sample data."""
    print("Populating test database...")

    # Create a user
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        user.set_password("admin123")
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"User already exists: {user.username}")

    # Create categories
    tech_category, _ = Category.objects.get_or_create(
        slug="technology",
        defaults={
            "name": "Technology",
            "description": "Posts about technology and programming",
        },
    )
    print(f"Created/found category: {tech_category.name}")

    design_category, _ = Category.objects.get_or_create(
        slug="design",
        defaults={
            "name": "Design",
            "description": "Posts about design and UX",
        },
    )
    print(f"Created/found category: {design_category.name}")

    # Create tags
    django_tag, _ = Tag.objects.get_or_create(
        slug="django", defaults={"name": "Django"}
    )
    python_tag, _ = Tag.objects.get_or_create(
        slug="python", defaults={"name": "Python"}
    )
    web_tag, _ = Tag.objects.get_or_create(slug="web", defaults={"name": "Web"})
    print("Created/found tags: Django, Python, Web")

    # Create posts
    post1, created = Post.objects.get_or_create(
        slug="getting-started-django",
        defaults={
            "title": "Getting Started with Django",
            "author": user,
            "category": tech_category,
            "content": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. In this post, we'll explore the basics of Django and how to get started with your first project.",
            "excerpt": "Learn the basics of Django and start your first project.",
            "status": "published",
            "published_at": timezone.now(),
            "featured": True,
        },
    )
    if created:
        post1.tags.add(django_tag, python_tag, web_tag)
        print(f"Created post: {post1.title}")

    post2, created = Post.objects.get_or_create(
        slug="python-best-practices",
        defaults={
            "title": "Python Best Practices",
            "author": user,
            "category": tech_category,
            "content": "Writing clean, maintainable Python code is essential for any developer. In this article, we'll cover best practices including PEP 8 style guide, type hints, documentation, and testing strategies.",
            "excerpt": "Essential best practices for writing clean Python code.",
            "status": "published",
            "published_at": timezone.now(),
        },
    )
    if created:
        post2.tags.add(python_tag)
        print(f"Created post: {post2.title}")

    post3, created = Post.objects.get_or_create(
        slug="web-design-trends",
        defaults={
            "title": "Web Design Trends 2025",
            "author": user,
            "category": design_category,
            "content": "The web design landscape is constantly evolving. Let's explore the latest trends in web design for 2025, including minimalism, dark mode, and accessibility-first design.",
            "excerpt": "Explore the latest web design trends for 2025.",
            "status": "draft",
        },
    )
    if created:
        post3.tags.add(web_tag)
        print(f"Created post: {post3.title}")

    # Create comments
    comment1, created = Comment.objects.get_or_create(
        post=post1,
        author=user,
        defaults={
            "content": "Great introduction to Django! Very helpful for beginners.",
            "is_approved": True,
        },
    )
    if created:
        print(f"Created comment on: {post1.title}")

    print("\nDatabase populated successfully!")
    print(f"Users: {User.objects.count()}")
    print(f"Categories: {Category.objects.count()}")
    print(f"Posts: {Post.objects.count()}")
    print(f"Tags: {Tag.objects.count()}")
    print(f"Comments: {Comment.objects.count()}")


if __name__ == "__main__":
    populate()
