const url = `${process.env.PRIMEAGENT_URL ?? ""}/api/v1/projects/${process.env.PROJECT_ID ?? ""}`;

const options = {
  method: 'DELETE',
  headers: {
    "accept": `*/*`,
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
