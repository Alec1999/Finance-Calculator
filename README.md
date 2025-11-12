# Finance-Calculator
Video Demo: https://www.youtube.com/watch?v=Epay-cgYC9o

Description:

Investment Insight is an interactive web application designed to provide users with important financial information. It provides an overview of investing for beginners, going over the different ways to invest, an interactive calculator to help them figure out the returns they can expect from an investment, and information about compound interest, and why it is so important.

The main feature of the web application is the interactive investment calculator. This allows users to input their initial investment amount, interest rate, and investment duration to calculate and visualize potential returns.

The home page has educational content in the form of bulleted items, going in-depth about the most common ways to invest, what the pros and cons are of each of those investments, and what rate of return is reasonable to expect from them. At the end, there is also some information about alternative investments, and the risks associated with those. There are also custom error messages that appear depending on what kind of input the user puts in (ie. no input, words instead of digits, numbers that are too large, etc.).

The third page explains the concept of compound interest, and gives a potential real-world scenario depicting how much of a difference it can make for investors.

The application has a responsive design that is formatted to work on both desktop and mobile devices, ensuring a seamless user experience. The navigation bar has been designed in a way that makes it easy to navigate to any one specific page, while not taking up too much room. Because of the length of the home page, I made the decision for the nav bar to stick to the top of the page, rather than forcing the user to scroll back up to the top.

I used bootstrap to achieve this, making sure that everything had a uniform design, and that the layout would adapt to different screen sizes. This also allowed me to set a specific variable depending on whichever page was last loaded, so I could dynamically change the navbar to highlight the current page.

The main feature is the investment calculator, which uses python functions to store the values, looping over those values for each year the user entered, figuring out the math for the rate of return, and adding everything back together, before sending all the information over to the html page displaying them. When the user hits the calculate button, a google donut chart shows what percentage of their final balance is their starting amount, their total contributions, and the total interest they would earn. The use of JavaScript enables real-time updates and visualizations.

Below the google chart is a table, showing more categories for each year the user had their investment. The variables were stored in a dictionary for each year, and then passed through to the html table using jinja syntax.

Everything was formatted on the html page to make sure all the numbers on the calculator page were formatted in USD. Special care went into making sure floating point precision didn’t affect the math for the calculator.

The compound interest page has more paragraph and header tags, and shows another google chart, this time a line graph. It shows how much money two different investors made over a period of 45 years. I altered the chart so that it would show both investors money while it was highlighted, and at any point on the graph, instead of just over each 10 year period.

At the bottom of each page is a footer, which goes over a financial disclosure. I made sure it would stick to the bottom of the page, so that it doesn’t interfere with the rest of the web application.

I chose a color scheme that was easy on the eyes, and not too flashy. Because the topic of the website is financial, I wanted colors that represented professionalism. The charts that I included are the most color parts, drawing the eyes to them.

# File Breakdown

My project has three total folders. The first of which is a file named ‘project’ which contains everything. The other two folders are named static, and templates. Inside of static I had two files, one of which was my css file, and the other was my java script file. The javascript file only ran a function to format the numbers the user would enter to have commas in the form of USD. The templates folder had all of my html files.

The first html file is layout.html. This serves as the base template for the application, providing a consistent structure for all pages. It contained a header with the navigation bar, a main content area, and a footer. It also linked bootstrap, and my other files such as the css. All other html files extend this one.

The second file is home.html. This page provided an overview of what the application was about, and had information about investments. It starts off with a bold header, an image depecting investing, and a sub title, with my name and the date and time it was published.

The third file is calculator.html. This page featured the interactive investment calculator, which would dynamically update as the user input their information.

The fourth page was calculator_submitted.html. At first, I only had one html page for the calculator, using an if statement to display the chart and table after the user would input information. However I ran into issues when designing the error messages that would appear if the user put incorrect information in. My solution was to create a second page that would extend the first, while also including the results information. Linking this page fixed the issue.

The fifth and final html file is compound_interest.html, which has information about compound interest for the user to read, as well as an interactive google chart for the user to see an example for investors.

The only other file is my python file, which just sits inside of the project folder on its own. I used flask to create routes in the python file for each page. Other than the routes, its main purpose is to run the investment calculator.

Originally created for Harvard’s CS50 course under my old GitHub account.
