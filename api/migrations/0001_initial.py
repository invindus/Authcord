# Generated by Django 5.0.2 on 2024-03-20 16:23

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('extern_id', models.CharField(blank=True, max_length=1024, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('github', models.URLField(blank=True)),
                ('profile_image', models.URLField(blank=True)),
                ('remote_name', models.CharField(max_length=1024, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('following', models.ManyToManyField(related_name='follows', to='api.author')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('object_type', models.CharField(choices=[('post', 'post'), ('comment', 'comment')], max_length=20, null=True)),
                ('object_id', models.CharField(max_length=36, null=True)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.author')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('host', models.URLField(max_length=1024, unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('our_username', models.CharField(blank=True, max_length=128, null=True)),
                ('our_password', models.CharField(blank=True, max_length=128, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.node'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
                ('data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='api.author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.TextField()),
                ('source', models.URLField(blank=True, max_length=1024)),
                ('origin', models.URLField(blank=True, max_length=1024)),
                ('extern_id', models.UUIDField(blank=True, null=True)),
                ('description', models.TextField()),
                ('content_type', models.CharField(choices=[('t', 'text/plain'), ('m', 'text/markdown'), ('b', 'text/base64'), ('p', 'image/png;base64'), ('j', 'image/jpeg;base64')], max_length=1)),
                ('content', models.TextField()),
                ('count', models.IntegerField(default=0)),
                ('comments', models.URLField(blank=True)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('visibility', models.CharField(choices=[('p', 'PUBLIC'), ('f', 'FRIENDS'), ('u', 'UNLISTED')], max_length=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.author')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('extern_id', models.CharField(blank=True, max_length=1024, null=True)),
                ('comment', models.TextField()),
                ('content_type', models.CharField(choices=[('t', 'text/plain'), ('m', 'text/markdown'), ('b', 'text/base64'), ('p', 'image/png;base64'), ('j', 'image/jpeg;base64')], default='t', max_length=100)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_comments', to='api.author')),
                ('node', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.node')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comments', to='api.post')),
            ],
        ),
    ]
