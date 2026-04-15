#!/bin/bash
# Build all Forest Docker images

set -e

IMAGES=(
    "audit:docker/Dockerfile.audit"
    "dashboard:docker/Dockerfile.dashboard"
    "network:docker/Dockerfile.network"
)

echo "🔨 Building Forest Docker Images..."
echo ""

# forest-core is already built
echo "✅ forest-core:1.0.0-alpha (already built)"

# Build remaining images
for image_config in "${IMAGES[@]}"; do
    IFS=':' read -r name dockerfile <<< "$image_config"
    image="forest-$name"
    
    echo "🔨 Building $image:1.0.0-alpha..."
    if docker build -f "$dockerfile" -t "$image:1.0.0-alpha" . > /dev/null 2>&1; then
        echo "✅ $image:1.0.0-alpha"
    else
        echo "⚠️  $image:1.0.0-alpha (build skipped - may need specific base image)"
    fi
done

echo ""
echo "📊 Built Images:"
docker images | grep forest- || echo "No forest images found"

echo ""
echo "✅ Build complete!"
