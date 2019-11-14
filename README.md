# Chicken Coop Control Automation and API

## Why?

Modern chickens require modern solutions. If your chickens live in a luxurious chicken mansion equipped with its own Raspberry Pi web server, then you'll need some code to automatically control their modern conveniences: lights, doors, cameras, etc.

## What?

This provides:
* A daily update of sunrise and sunset based on latitude and longitude
* Automatic scheduling for powering up doors and lights
* A REST API to provide manual control and status information on these items

This does not provide:
* Hardware: certain assumptions have been made about the hardware setup. See (link to docs here)
* A Web UI: See https://github.com/isometimescode/coopcontrol-react to install that separately
* Security: There are no passwords or other method of security offered with these APIs and it is assumed that your web server is not publicly accessible.

## Getting Started

1. General Requirements
2. Installation
3. Configuration
4. Testing

## Attribution

**Sunrise/Sunset Data:** https://sunrise-sunset.org/api
