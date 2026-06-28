# Vertical Runtime Adapter

## Purpose

This phase turns static vertical case packs into executable state definition requests.

The adapter reads:

- vertical manifest;
- domain map;
- entity map;
- gate map;
- operational cube seed;
- sample intake or state prompt.

It generates structured JSON and markdown requests that the product runtime can later process through API/UI.

## Safety

The adapter never authorizes implementation, production activation or client-facing claims.
