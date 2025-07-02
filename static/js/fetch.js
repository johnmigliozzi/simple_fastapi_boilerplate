// Accept any URL and return a JS object from a JSON API
async function getJsonApiResponse(url) {
    try {
        const response = await fetch(url);
        if (response.status === 401) {
            uiSetLogout();
        }
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        return await response.json();
    }
    catch (error) {
        console.error(error.message);
        return null;
    }
}