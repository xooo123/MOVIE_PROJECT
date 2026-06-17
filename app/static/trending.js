async function loadTrending() {
    try {
        const response = await fetch("/api/trending");
        const data = await response.json();

        showTrending(data.results);
    } catch (error) {
        console.log("Error:", error);
    }
}

function showTrending(movies) {
    const container = document.getElementById("trending");
    container.innerHTML = "";

    movies.forEach(movie => {
        const div = document.createElement("div");

        div.innerHTML = `
            <h3>${movie.title}</h3>
           <div><img src="https://image.tmdb.org/t/p/w200${movie.poster_path}"></div>
            <p>⭐ ${movie.vote_average}</p>
        `;

        container.appendChild(div);
    });
}

loadTrending();