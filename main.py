import ray
import csv
import os
import pickle
from playwright.sync_api import Error, sync_playwright, TimeoutError

from routines import extract_title_details, get_repda, go_to_title_details


ray.init(
    num_cpus=5,
)


titles_to_extract = []

with open("repda-consulta-basica-guanajuato-nov-2023.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        titles_to_extract.append(row)


@ray.remote(max_retries=15)
def extract(title: str, date: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
        )
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        try:
            get_repda(page)
            go_to_title_details(page, title)
            data = extract_title_details(page, date)
        except TimeoutError:
            data = []
            print(f"TimeoutError: {title}")
        except IndexError:
            data = []
            print(f"IndexError: {title}")
        except Error as e:
            data = []
            print(f"Playwright error: {title}")
            print(e)
        except Exception as e:
            data = []
            print(f"Exception: {title}")
            print(e)
        context.close()
        browser.close()

        return data


results = []
print(f"Extracting {len(titles_to_extract)} titles")


# check if there is a checkpoint file
# if there is, load it and resume from there
# if not, start from 0

checkpoint = {
    "completed_batchs": 0,
    "results": [],
}

if os.path.isfile("checkpoint.pkl"):
    with open("checkpoint.pkl", "rb") as f:
        checkpoint = pickle.load(f)

checkpoint_batch = checkpoint["completed_batchs"]

print(f"Resuming from batch {checkpoint['completed_batchs']}")

results = checkpoint["results"]


batch_size = 100

for i in range(checkpoint_batch, len(titles_to_extract), batch_size):
    print(f"Batch {i / batch_size:0.0f} of {len(titles_to_extract) / batch_size:0.0f}")

    start = i
    if i + batch_size > len(titles_to_extract):
        print("Last batch")
        end = -1
    else:
        end = i + batch_size

    batch_titles = []

    batch_tasks = [
        extract.remote(title["Título"], title["Fecha de registro"])
        for title in titles_to_extract[start:end]
    ]

    for result in ray.get(batch_tasks):
        results.extend(result)

    print(f"Batch {i / batch_size:0.0f} completed")
    print(f"Total results: {len(results)}")
    print("Saving checkpoint")
    # save checkpoint
    checkpoint = {
        "completed_batchs": i + batch_size,
        "results": results,
    }

    with open("checkpoint.pkl", "wb") as f:
        pickle.dump(checkpoint, f)

    print("Saving partial results")

    with open("partial/partial_results.json", "w") as f:
        f.write("[\n")
        for result in results:
            f.write(result.json())
            f.write(",\n")
        f.write("]\n")
    print("Partial results saved")
    print("=" * 80)
    print("Getting next batch")

print("All batches completed")

# save results

print("Saving results")

all_titles = set([title["Título"] for title in titles_to_extract])
crawled_titles = set([result.titulo for result in results])

missing_titles = all_titles - crawled_titles

# write missing titles to file
with open("missing_titles.csv", "w") as f:
    f.write("Título,Fecha de registro\n")
    for title in missing_titles:
        # find the title in the original list
        for row in titles_to_extract:
            if row["Título"] == title:
                f.write(f"{row['Título']},{row['Fecha de registro']}\n")


with open("results.json", "w") as f:
    f.write("[\n")
    for result in results:
        f.write(result.json())
        f.write(",\n")
    f.write("]\n")

print("Results saved")
print("Crawling completed")
