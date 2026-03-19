#!/bin/bash
set -euo pipefail

# =============================================================================
# No YouTube Shorts — Deployment Script (macOS Safari Extension)
# Usage:
#   ./scripts/deploy.sh appstore      — Archive, export, upload to App Store Connect
#   ./scripts/deploy.sh archive       — Archive + export .pkg only (no upload)
#   ./scripts/deploy.sh bump 1.1.0    — Update MARKETING_VERSION in project
#   ./scripts/deploy.sh notarize      — Archive, export, notarize for direct distribution
# =============================================================================

# -- Configuration (fill in once) ---------------------------------------------
API_KEY_ID="32LF4Q3Z7N"          # App Store Connect > Users & Access > Integrations > API Keys
API_ISSUER_ID="3c8dce31-6803-4d23-ba4f-48dab97d8d98"       # Same page, shown at top
APP_APPLE_ID="6760815295"        # Numeric ID from App Store Connect app record
BUNDLE_ID="com.prodius.No-YouTube-Shorts"
# -----------------------------------------------------------------------------

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
XCODEPROJ="$PROJECT_DIR/No YouTube Shorts.xcodeproj"
SCHEME="No YouTube Shorts"
EXPORT_OPTIONS="$PROJECT_DIR/ExportOptions.plist"
BUILD_DIR="$PROJECT_DIR/build"
ARCHIVE_DIR="$BUILD_DIR/archive"
EXPORT_DIR="$BUILD_DIR/export"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}[INFO]${NC} $1" >&2; }
success() { echo -e "${GREEN}[OK]${NC} $1" >&2; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# -- Helpers ------------------------------------------------------------------

get_marketing_version() {
    # Read from pbxproj — first MARKETING_VERSION found
    grep 'MARKETING_VERSION' "$XCODEPROJ/project.pbxproj" \
        | head -1 \
        | sed 's/.*= *\([^;]*\);/\1/' \
        | tr -d ' "'
}

generate_build_number() {
    date +"%Y%m%d%H%M"
}

check_prerequisites() {
    info "Checking prerequisites..."

    command -v xcodebuild >/dev/null 2>&1 || error "Xcode command line tools not installed. Run: xcode-select --install"
    [ -d "$XCODEPROJ" ] || error "Xcode project not found at $XCODEPROJ"
    [ -f "$EXPORT_OPTIONS" ] || error "ExportOptions.plist not found at $EXPORT_OPTIONS"

    success "Prerequisites OK"
}

check_upload_prerequisites() {
    [ -n "$API_KEY_ID" ] || error "API_KEY_ID not set. Edit the configuration section in this script."
    [ -n "$API_ISSUER_ID" ] || error "API_ISSUER_ID not set. Edit the configuration section in this script."

    local key_path="$HOME/.appstoreconnect/private_keys/AuthKey_${API_KEY_ID}.p8"
    [ -f "$key_path" ] || error "API key file not found at $key_path\nDownload from App Store Connect > Users & Access > Integrations > API Keys"

    success "Upload prerequisites OK"
}

clean_build() {
    info "Cleaning build artifacts..."
    rm -rf "$BUILD_DIR"
    xcodebuild clean \
        -project "$XCODEPROJ" \
        -scheme "$SCHEME" \
        -configuration Release \
        -quiet 2>/dev/null || true
    success "Clean complete"
}

archive() {
    local version="$1"
    local build_number="$2"
    local archive_path="$ARCHIVE_DIR/NoYouTubeShorts-${version}-${build_number}.xcarchive"

    info "Archiving No YouTube Shorts v${version} (${build_number})..."
    mkdir -p "$ARCHIVE_DIR"

    xcodebuild archive \
        -project "$XCODEPROJ" \
        -scheme "$SCHEME" \
        -configuration Release \
        -destination "generic/platform=macOS" \
        -archivePath "$archive_path" \
        -allowProvisioningUpdates \
        MARKETING_VERSION="$version" \
        CURRENT_PROJECT_VERSION="$build_number" \
        2>&1 | tail -5

    [ -d "$archive_path" ] || error "Archive failed — .xcarchive not found at $archive_path"

    success "Archive created: $archive_path"
    RESULT_PATH="$archive_path"
}

export_app() {
    local archive_path="$1"

    info "Exporting app..."
    mkdir -p "$EXPORT_DIR"

    xcodebuild -exportArchive \
        -archivePath "$archive_path" \
        -exportPath "$EXPORT_DIR" \
        -exportOptionsPlist "$EXPORT_OPTIONS" \
        -allowProvisioningUpdates

    # For macOS, the export produces a .pkg or .app
    local pkg_path
    pkg_path=$(find "$EXPORT_DIR" -name "*.pkg" -maxdepth 1 | head -1)

    if [ -n "$pkg_path" ] && [ -f "$pkg_path" ]; then
        local pkg_size
        pkg_size=$(du -sh "$pkg_path" | cut -f1)
        success "Package exported: $pkg_path ($pkg_size)"
        RESULT_PATH="$pkg_path"
    else
        # Fall back to .app
        local app_path
        app_path=$(find "$EXPORT_DIR" -name "*.app" -maxdepth 1 | head -1)
        [ -n "$app_path" ] && [ -d "$app_path" ] || error "Export failed — no .pkg or .app found in $EXPORT_DIR"
        success "App exported: $app_path"
        RESULT_PATH="$app_path"
    fi
}

upload() {
    local package_path="$1"
    local version="$2"
    local build_number="$3"

    info "Uploading to App Store Connect..."

    xcrun altool --upload-package "$package_path" \
        --type macos \
        --apple-id "$APP_APPLE_ID" \
        --bundle-id "$BUNDLE_ID" \
        --bundle-version "$build_number" \
        --bundle-short-version-string "$version" \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID" \
        || error "Upload to App Store Connect failed"

    success "Upload complete!"
    echo ""
    info "Check build status at: https://appstoreconnect.apple.com/apps"
    info "Builds typically process in 15-30 minutes."
}

# -- Commands -----------------------------------------------------------------

cmd_deploy() {
    check_prerequisites
    check_upload_prerequisites

    local version
    version=$(get_marketing_version)
    local build_number
    build_number=$(generate_build_number)

    [ -n "$APP_APPLE_ID" ] || error "APP_APPLE_ID not set. Create the app record in App Store Connect first, then set it in this script."

    info "Deploying No YouTube Shorts v${version} (${build_number}) → App Store"
    echo ""

    clean_build

    archive "$version" "$build_number"
    local archive_path="$RESULT_PATH"

    export_app "$archive_path"
    local package_path="$RESULT_PATH"

    upload "$package_path" "$version" "$build_number"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN} No YouTube Shorts v${version} (${build_number})${NC}"
    echo -e "${GREEN} Successfully uploaded to App Store!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

cmd_archive() {
    check_prerequisites

    local version
    version=$(get_marketing_version)
    local build_number
    build_number=$(generate_build_number)

    info "Archiving No YouTube Shorts v${version} (${build_number})..."
    echo ""

    clean_build

    archive "$version" "$build_number"
    local archive_path="$RESULT_PATH"

    export_app "$archive_path"
    local package_path="$RESULT_PATH"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN} Archive complete!${NC}"
    echo -e "${GREEN} Package: ${package_path}${NC}"
    echo -e "${GREEN}========================================${NC}"
}

cmd_bump() {
    local new_version="${1:-}"
    [ -n "$new_version" ] || error "Usage: ./scripts/deploy.sh bump <version>\nExample: ./scripts/deploy.sh bump 1.1.0"

    # Validate semver format
    if ! echo "$new_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        error "Invalid version format: $new_version (expected X.Y.Z)"
    fi

    local current_version
    current_version=$(get_marketing_version)

    info "Bumping version: ${current_version} → ${new_version}"

    # Update all MARKETING_VERSION entries in pbxproj
    sed -i '' "s/MARKETING_VERSION = [^;]*/MARKETING_VERSION = ${new_version}/" "$XCODEPROJ/project.pbxproj"

    success "Version bumped to ${new_version}"
}

# -- Main ---------------------------------------------------------------------

command="${1:-help}"
shift || true

case "$command" in
    appstore)
        cmd_deploy
        ;;
    archive)
        cmd_archive
        ;;
    bump)
        cmd_bump "$@"
        ;;
    help|--help|-h)
        echo "No YouTube Shorts — Deployment Script"
        echo ""
        echo "Usage: ./scripts/deploy.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  appstore          Archive, export, and upload to App Store Connect"
        echo "  archive           Archive and export only (no upload)"
        echo "  bump <version>    Update MARKETING_VERSION (e.g., bump 1.1.0)"
        echo "  help              Show this help message"
        echo ""
        echo "Configuration:"
        echo "  Edit the top of this script to set API_KEY_ID, API_ISSUER_ID, APP_APPLE_ID"
        echo "  Place your .p8 key at: ~/.appstoreconnect/private_keys/AuthKey_<KEYID>.p8"
        ;;
    *)
        error "Unknown command: $command\nRun './scripts/deploy.sh help' for usage."
        ;;
esac
