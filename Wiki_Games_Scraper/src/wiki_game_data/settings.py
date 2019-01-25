BOT_NAME = 'wiki_game_data'
SPIDER_MODULES = ['wiki_game_data.spiders']
NEWSPIDER_MODULE = 'wiki_game_data.spiders'
ITEM_PIPELINES = {
    'wiki_game_data.pipelines.JsonWithEncodingPipeline' : 100,
}
FEED_EXPORT_ENCODING = 'utf-8'
DOWNLOAD_DELAY = 0.5