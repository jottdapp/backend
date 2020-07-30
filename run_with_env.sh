#!/bin/bash
export $(cat .env | xargs)
uvicorn main:app
