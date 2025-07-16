from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore",
                                      case_sensitive=False)


class StickersSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='sticker_')
    sbu_file_id: str = 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA'
    porohobot_file_id: str = 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME'
    zelebot_file_id: str = 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE'
    night_file_id: str = 'CAACAgIAAxkBAAEKWq5lDOyAX1vNodaWsT5amK0vGQe_ggACHCkAAspLuUtESxXfKFwfWTAE'


class DbSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='db_')
    user: str
    password: SecretStr
    host: str
    port: int
    name: str

    def get_url(self) -> str:
        return (f'postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}'
                f'@{self.host}:{self.port}/{self.name}')


class ToxicitySettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='toxic_')
    api_key: SecretStr
    api_url: str = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze'
    threshold: float = 0.6
    reaction: str = '😈'
    level_texts: dict[int, str] = {
        10: 'Добрый чел позитивный',
        40: 'Норм чел',
        100: 'С гнильцой человек',
        200: 'Неадекват ебаный',
        400: 'Опасен для общества, изолируйте нахуй',
        900: 'Представляет прямую угрозу национальной безопасности Украины. Все сообщения переданы в СБУ',
        1500: 'Подлежит устранению согласно решению Собвеза ООН',
        999999: 'Классифицирован как SCP-███'
    }


class Settings(ConfigBase):
    bot_token: SecretStr
    webhook_domain: str
    host: str = '0.0.0.0'
    port: int = 80
    report_chat_id: int
    paint_web_app_url: str
    time_zone: str = 'UTC'
    toxic: ToxicitySettings = Field(default_factory=ToxicitySettings)
    db: DbSettings = Field(default_factory=DbSettings)
    stickers: StickersSettings = Field(default_factory=StickersSettings)


settings = Settings()
print(settings.db.get_url())
