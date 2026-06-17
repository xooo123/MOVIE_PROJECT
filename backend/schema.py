from pydantic import BaseModel, Field
class MovieInput(BaseModel):
    numVotes: float= Field(..., ge= 0, le= 10000)
    genre: str
    avg_actor_score: float= Field(..., ge= 0, le= 10)
    writer_avg_score: float= Field(..., ge= 0, le= 10)
    director_avg_score: float= Field(..., ge= 0, le= 10)