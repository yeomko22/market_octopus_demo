gcloud functions deploy market-octopus-news-search \
--gen2 \
--runtime=python311 \
--region=asia-northeast3 \
--source=. \
--entry-point=run \
--allow-unauthenticated \
--trigger-http \
--env-vars-file=.env.yaml \
--serve-all-traffic-latest-revision \
--memory=1024MB \
--max-instances=5

