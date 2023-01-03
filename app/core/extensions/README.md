# core/extensions
This folder includes some useful "extensions" to Django itself that answer common patterns or fix existing things. They can be imported directly from their own modules.

It's also recommended that core.extensions.models.BaseAbstractModel class is used as a basis for all models, providing a UUID primary key, multiple metadata fields (created, last updated, ...) and soft deletion.
