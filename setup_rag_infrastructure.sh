#!/bin/bash

# ===== Project / Region =====
export PROJECT_ID="coolbits-og-bridge"
export REGION="europe-west3"
export LOCATION="$REGION"

# ===== Naming =====
export AR_REPO="ogrok-repo"
export BASE_PREFIX="ogrok"
export TOPIC="agent-comm"

# ===== Cloud SQL (Postgres + pgvector) =====
export SQL_INSTANCE="pg-rag"
export SQL_DB="ragdb"
export SQL_USER="raguser"
export SQL_VERSION="POSTGRES_15"
export SQL_TIER="db-custom-2-7680"
export SQL_PASS="$(openssl rand -base64 24)"

# ===== Networking =====
export VPC_NET="default"
export VPC_CONNECTOR="svpc-${REGION}"

# ===== Roles list (ogrok01..ogrok12) =====
export ROLES=$(printf "ogrok%02d " $(seq 1 12))

echo "🚀 Starting RAG setup for $PROJECT_ID in $REGION..."
echo "📋 Roles: $ROLES"

# Enable APIs & basic config
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
gcloud config set artifacts/location $LOCATION

gcloud services enable \
  run.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  pubsub.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

echo "✅ APIs enabled successfully"

# Artifact Registry
gcloud artifacts repositories create $AR_REPO \
  --repository-format=docker \
  --location=$LOCATION \
  --description="Containers ogrok agents"

gcloud auth configure-docker ${LOCATION}-docker.pkg.dev

echo "✅ Artifact Registry created"

# Serverless VPC Access + Private Service Connect
gcloud compute addresses create google-managed-services-$VPC_NET \
  --global --purpose=VPC_PEERING \
  --addresses=10.9.0.0 --prefix-length=24 \
  --network=$VPC_NET

gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --network=$VPC_NET \
  --ranges=google-managed-services-$VPC_NET

gcloud compute networks vpc-access connectors create $VPC_CONNECTOR \
  --region=$REGION \
  --network=$VPC_NET \
  --range=10.8.0.0/28

echo "✅ VPC networking configured"

# Cloud SQL Postgres + pgvector
gcloud sql instances create $SQL_INSTANCE \
  --database-version=$SQL_VERSION \
  --region=$REGION \
  --tier=$SQL_TIER \
  --network=$VPC_NET \
  --no-assign-ip \
  --availability-type=REGIONAL \
  --backup-start-time=02:00

gcloud sql databases create $SQL_DB --instance=$SQL_INSTANCE
gcloud sql users create $SQL_USER --instance=$SQL_INSTANCE --password="$SQL_PASS"

export SQL_CONN_NAME="$(gcloud sql instances describe $SQL_INSTANCE --format='value(connectionName)')"
echo "✅ Cloud SQL created: $SQL_CONN_NAME"

# Secret Manager
printf '%s' "$SQL_PASS"        | gcloud secrets create sql-pass --data-file=-
printf '%s' "$SQL_USER"        | gcloud secrets create sql-user --data-file=-
printf '%s' "$SQL_DB"          | gcloud secrets create sql-db   --data-file=-
printf '%s' "$SQL_CONN_NAME"   | gcloud secrets create sql-conn --data-file=-

echo "✅ Database secrets created"

# Pub/Sub
gcloud pubsub topics create $TOPIC
echo "✅ Pub/Sub topic created"

# Buckets RAG + Vertex AI Search datastore
for R in $ROLES; do
  gsutil mb -p $PROJECT_ID -l $LOCATION gs://cb-rag-${R}
  
  gcloud discovery-engine data-stores create rag-${R} \
    --location=$REGION \
    --project=$PROJECT_ID \
    --display-name="rag-${R}" \
    --industry-vertical=GENERIC \
    --solution-types=SEARCH

  gcloud discovery-engine data-stores connectors create \
    --project=$PROJECT_ID \
    --location=$REGION \
    --data-store=rag-${R} \
    --display-name="gcs-${R}" \
    --gcs-source="gs://cb-rag-${R}/"
    
  echo "✅ Created RAG resources for $R"
done

echo "🎉 RAG infrastructure setup complete!"
echo "📊 Next: Create service account and deploy Cloud Run services"
