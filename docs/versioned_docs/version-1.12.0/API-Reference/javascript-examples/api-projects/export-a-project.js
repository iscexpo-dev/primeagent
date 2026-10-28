const url = `${process.env.PRIMEAGENT_URL ?? ""}/api/v1/projects/download/${process.env.PROJECT_ID ?? ""}`;

const options = {
  method: 'GET',
  headers: {
    "accept": `application/json`,
    "x-api-key": `${process.env.PRIMEAGENT_API_KEY ?? ""}`,
  },
};

fetch(url, options)
  .then(async (response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.arrayBuffer();
    console.log("Received binary response for primeagent-project.zip", data.byteLength);
  })
  .catch((error) => console.error(error));
