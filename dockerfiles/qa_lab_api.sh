start_api()
{
	uvicorn unittestapi:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
}



start_api