# Corporatica Flask Task
the generally covered the main three points

1.Tabular Data:

    ○ CRUD operations(Create,Read,Update,Delete)CSV Files.
    ○ API for computing advanced statistics (mean, median, mode,
    quartiles, outliers)

2.RGB Images:

    ○ CRUD Operations (Create,Read, Update,Delete).

    ○  API for generating color histograms and segmentation masks,
    with APIs to adjust parameters and retrieve results.



3.Textual Data:

    ○ Api for generating Text Summarization
    ○ Api for keyword extraction, 
    ○ Api for  basic analyze_sentiment.
    ○ Api for tsne_display





## The Steps:

git clone https://github.com/yassenTA/corporatica.git

cd flask_project_main

pip install -r requirements.txt

python run.py 

write http://127.0.0.1:5000/docs/ in your browser to open the swagger 

## API Documentation
    1.Tabular Data :
      ○ Create a Tabular : http://127.0.0.1:5000/docs/#/Tabular/post_api_tabular_create_tabular
      ○ Update Tabular :http://127.0.0.1:5000/docs/#/Tabular/put_api_tabular_update_tabular__id_
      ○ Delete Tabular :http://127.0.0.1:5000/docs/#/Tabular/delete_api_tabular_delete_tabular__id_
      ○ Get a Statistics From Specific Tabular File : http://127.0.0.1:5000/docs/#/Tabular/get_api_tabular_get_tabular__id_
      ○ List All tabular : http://127.0.0.1:5000/docs/#/Tabular/get_api_tabular_list_all_tabular
    2. Image:
      ○ Create Image :http://127.0.0.1:5000/docs/#/Image/post_api_image_create_image
      ○ Update Image : http://127.0.0.1:5000/docs/#/Image/put_api_image_update_image__id_
      ○ Image and Generating Color Histograms and Segmentation Masks:http://127.0.0.1:5000/docs/#/Image/get_api_image_get_image__id_
      ○ List all images: http://127.0.0.1:5000/docs/#/Image/get_api_image_list_all_images
    3. Text:
      ○ text_analysis :http://127.0.0.1:5000/docs/#/Text/post_api_text_analyze_sentiment
      ○ Extract_Keywords :http://127.0.0.1:5000/docs/#/Text/post_api_text_extract_keywords
      ○ text_Summarizes : http://127.0.0.1:5000/docs/#/Text/post_api_text_summarize_text
      ○ TSNE Display : http://127.0.0.1:5000/docs/#/Text/post_api_text_tsne_display
    4. Authentication :
        ○ Register : http://127.0.0.1:5000/docs/#/Authentication/post_api_user_register
        ○ Login :http://127.0.0.1:5000/docs/#/Authentication/post_api_user_login
        ○ Logout : http://127.0.0.1:5000/docs/#/Authentication/post_api_user_logout 
## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any inquiries or support, feel free to reach out to yassenTA.
