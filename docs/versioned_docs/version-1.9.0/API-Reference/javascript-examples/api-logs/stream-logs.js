const url = `${process.env.PRIMEAGENT_URL ?? ""}/logs-stream`;

const options = {
  method: 'GET',
  headers: {
    "accept": `text/event-stream`,
    "x-api-key": `${process.env.PRIMEAGENT_API_KEY ?? ""}`,
  },
};

fetch(url, options)
  .then(async (response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const text = await response.text();
    console.log(text);
  })
  .catch((error) => console.error(error));
