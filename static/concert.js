async function showMatchingSection() {
    const matchingSection = document.querySelector('.matching');
    matchingSection.style.display = 'none';

    await generateNewBuddy();  

    matchingSection.style.display = 'block';
}

async function generateNewBuddy() {
    try {
        const response = await fetch('/api/buddy/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            try {
                // Try to get JSON error if available
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok');
            } catch (jsonError) {
                // If JSON parsing fails, throw generic error
                throw new Error('Network response was not ok');
            }
        }

        const data = await response.json();
        console.log("Im data", data)
        const recommendedUserIds = data.recommended_user_ids.id;
        console.log(recommendedUserIds)
        // Only select one
        if (recommendedUserIds) {
            console.log(recommendedUserIds)
            await updateCardWithNewUser(recommendedUserIds);  // Await the update
        } else {
            alert('No new recommendations available!');
        }

    } catch (error) {
        console.error('Error fetching new buddy:', error);
    }
}



async function updateCardWithNewUser(userId) {
    try {
        // Call the backend to get user information
        const response = await fetch(`/api/user-info/${userId}`);
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const userData = await response.json();
        let formattedGenres = '';
        if (Array.isArray(userData.music_genre) && userData.music_genre.length > 0) {
            formattedGenres = userData.music_genre.join(', ');  
        } else {
            formattedGenres = 'Not specified'; 
        }

        // Format the card content with user information
        const formattedText = `Hey, my name is ${userData.user_name}! I am from ${userData.user_location}, and I love listening to ${formattedGenres}.`;

        console.log("I am userData", userData)

        // Update card content with the fetched user data
        document.querySelector('.card-title').textContent = userData.user_name || 'Unknown User';
        document.querySelector('.card-text').textContent = formattedText || 'No description available.';
        
        if (userData.image_url) {
            document.querySelector('#card-img').src = userData.image_url;
        }

    } catch (error) {
        console.error('Error updating card content:', error);
    }
}